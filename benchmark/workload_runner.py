import logging
import queue
import threading
import time
import typing

import kubernetes
from kubernetes import client
from kubernetes.client import rest


class WorkloadRunner(object):

    def __init__(self, core_api: client.CoreV1Api, dry_run: bool = False):
        self.client = core_api
        self.api_client = self.client.api_client
        self.run_threads: typing.List[JobRunningThread] = []
        self.dry_run = dry_run

    def has_done(self) -> bool:
        return all([not rt.is_alive() for rt in self.run_threads])

    def restart(self, workload):
        self.stop()
        self.start(workload)

    def delete_workload_exists_in_cluster(self):
        try:
            self.client.delete_collection_namespaced_pod('default',
                                                         grace_period_seconds=0,
                                                         propagation_policy='Foreground')
        except rest.ApiException as e:
            logging.warning("Met an error when deleting pods: %s." % e)

    def start(self, workload):
        for job in workload:
            run_thread = JobRunningThread(self.client, job, self.dry_run, daemon=True)
            run_thread.start()
            self.run_threads.append(run_thread)

    def stop(self):
        for thread in self.run_threads:
            if thread.is_alive():
                thread.stop()

        self.delete_workload_exists_in_cluster()
        wait_sum = 0
        wait_interval = 5
        while not self._all_job_deleted():
            time.sleep(wait_interval)
            wait_sum += wait_interval
            logging.info('Waiting pods to be deleted (%d seconds).' % wait_sum)

        for thread in self.run_threads:
            thread.join()
        self.run_threads.clear()

    def _all_job_deleted(self):
        return len(self.client.list_namespaced_pod('default').items) == 0


class JobRunningThread(threading.Thread):

    def __init__(self, api_client: client.CoreV1Api, job: dict, dry_run: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_flag = threading.Event()
        self.client = api_client
        self.job = job
        self.dry_run = dry_run
        self.queue = queue.Queue()
        self._init_queue()
        self.job_name = ''

    def _init_queue(self):
        for job in self.job:
            self.queue.put(job)

    def run(self):
        current_time_ms = 0
        self.run_flag.set()
        while self.run_flag.is_set() and not self.queue.empty():
            self.run_flag.wait()
            job = self.queue.get()
            start_time_ms, pod = int(job['startTime']), job['pod']
            self.job_name = pod['metadata']['labels']['job']
            sleep_time_ms = start_time_ms - current_time_ms
            current_time_ms = start_time_ms
            if sleep_time_ms > 0:
                time.sleep(sleep_time_ms / 1000)

            if self.run_flag.is_set():
                name = pod['metadata']['name']
                task_type = pod['metadata']['labels']['taskType']
                logging.info('Creating pod: %s (job: %s, type: %s), time from thread start: %dms' %
                             (name, self.job_name, task_type, current_time_ms))
                self._start_single_pod_sync(pod)
        logging.info('Thread %s (%s) finished.' % (threading.current_thread().name, self.job_name))

    def _start_single_pod_sync(self, pod: client.V1Pod):
        while True:
            try:
                if self.dry_run:
                    kubernetes.utils.create_from_dict(self.client.api_client, pod, dry_run='All')
                else:
                    kubernetes.utils.create_from_dict(self.client.api_client, pod)
                return
            except Exception as e:
                if 'AlreadyExists' in str(e):
                    return
                logging.info(e)
                time.sleep(1)

    def stop(self):
        self.run_flag.clear()
