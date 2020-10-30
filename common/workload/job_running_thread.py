import logging
import queue
import threading
import time

import kubernetes
from kubernetes import client


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
