import logging
import time
import typing

from kubernetes import client
from kubernetes.client import rest

from .job_running_thread import JobRunningThread


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

        time.sleep(30)

        for thread in self.run_threads:
            thread.join()
        self.run_threads.clear()

    def _all_job_deleted(self):
        return len(self.client.list_namespaced_pod('default').items) == 0
