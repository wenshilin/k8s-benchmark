import logging
import queue
import time
from typing import Optional

from kubernetes.client import V1Pod

from .cache import Cache
from .event_handler_impl import EventHandlerImpl
from .informer import Informer
from ...utils import kube as utils


def create_pod_cache_and_start_listening(client, need_process_func, timeout=None,
                                         wait_init_seconds: int = 0, disable_log: bool = False):
    cache = PodCache(timeout, disable_log)
    informer = Informer(client.list_pod_for_all_namespaces)
    informer.add_event_handler(EventHandlerImpl(cache, need_process_func))
    informer.run()
    time.sleep(wait_init_seconds)
    return cache


class PodCache(object):

    def __init__(self, timeout=None, disable_log: bool = False):
        self._timeout = timeout
        self._disable_log = disable_log
        self._cache = Cache()
        self._finished_pods = []
        self._waiting_pod_ids = queue.Queue()

    def get_pod_by_uid(self, uid) -> Optional[str]:
        return self._cache.get(uid)

    def get_finished_pods_and_clean_cache(self):
        pods = self._finished_pods
        self.clean_finished_pods()
        return [p for p in pods if self.pod_exists(p)]

    def pod_exists(self, pod) -> bool:
        uid = utils.get_obj_uid(pod)
        return self.get_pod_by_uid(uid) is not None

    def push_back_waiting_pod(self, waiting_pod):
        self._waiting_pod_ids.put(utils.get_obj_uid(waiting_pod))

    def waiting_queue_empty(self):
        return self._waiting_pod_ids.empty()

    def get_next_pod(self, filter_func) -> Optional[V1Pod]:
        try:
            uid = self._waiting_pod_ids.get(timeout=self._timeout)
            pod = self.get_pod_by_uid(uid)
            while not pod or not filter_func(pod):
                uid = self._waiting_pod_ids.get(timeout=self._timeout)
                pod = self.get_pod_by_uid(uid)
            return pod
        except queue.Empty:
            return None

    def filter(self, func):
        return list(self._cache.filter(func))

    def add(self, obj, func):
        if func(obj):
            self._waiting_pod_ids.put(utils.get_obj_uid(obj))
        self._cache.put(utils.get_obj_uid(obj), obj)

    def update(self, new_obj):
        key = utils.get_obj_uid(new_obj)
        old_obj = self._cache.get(key)
        if old_obj is not None:
            old_state_is_not_finished = utils.pod_container_creating(old_obj) or \
                                        utils.pod_pending(old_obj) or \
                                        utils.pod_running(old_obj)
            finished = utils.pod_finished(new_obj) and old_state_is_not_finished
            failed = utils.pod_failed(new_obj) and utils.pod_pending(old_obj)
            if not self._disable_log and (finished or failed):
                logging.info(f'{utils.get_obj_name(new_obj)} {new_obj.status.phase}')
                self._finished_pods.append(new_obj)
        self._cache.put(key, new_obj)

    def delete(self, obj):
        self._cache.delete(utils.get_obj_uid(obj))

    def clean_finished_pods(self):
        self._finished_pods = []
