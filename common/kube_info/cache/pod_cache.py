import logging
import queue
import time
from datetime import datetime
from typing import Optional

from dateutil.tz import tz
from kubernetes.client import V1Pod

from .cache import Cache
from .event_handler_impl import EventHandlerImpl
from .informer import Informer
from ...utils import kube as utils


def create_pod_cache_and_start_listening(client, need_process_func, timeout=None, wait_init_seconds: int = 0):
    cache = PodCache(timeout)
    informer = Informer(client.list_pod_for_all_namespaces)
    informer.add_event_handler(EventHandlerImpl(cache, need_process_func))
    informer.run()
    time.sleep(wait_init_seconds)
    return cache


class PodCache(object):

    def __init__(self, timeout=None):
        self._timeout = timeout
        self._cache = Cache()
        self._finished_pods = []
        self._waiting_pod_ids = queue.Queue()

    def get_pods_by_node_name(self, node_name):
        return self.filter(lambda p: utils.get_pod_node_name(p) == node_name)

    def get_pod_by_uid(self, uid) -> Optional[str]:
        return self._cache.get(uid)

    def get_finished_pods_and_clean_cache(self):
        pods = self._finished_pods
        self.clean_finished_pods()
        return [(p, ft) for p, ft in pods if self.pod_exists(p)]

    def pod_exists(self, pod) -> bool:
        uid = utils.get_obj_uid(pod)
        return self.get_pod_by_uid(uid) is not None

    def push_back_waiting_pod(self, waiting_pod):
        self._waiting_pod_ids.put(utils.get_obj_uid(waiting_pod))

    def waiting_queue_empty(self):
        return self._waiting_pod_ids.empty()

    def waiting_count(self):
        return self._waiting_pod_ids.qsize()

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

    def get_all(self):
        return self._cache.get_all()

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
            finished = utils.pod_finished(new_obj) and utils.pod_running(old_obj)
            failed = utils.pod_failed(new_obj) and utils.pod_pending(old_obj)
            if finished or failed:
                logging.info(f'{utils.get_obj_name(new_obj)} {new_obj.status.phase}')
                self._finished_pods.append((new_obj, datetime.now(tz.tzutc())))
        self._cache.put(key, new_obj)

    def delete(self, obj):
        self._cache.delete(utils.get_obj_uid(obj))

    def clean_finished_pods(self):
        self._finished_pods = []
