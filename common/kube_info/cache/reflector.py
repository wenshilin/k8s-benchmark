from threading import Thread
from kubernetes.watch import Watch
from typing import List

from .event_handler import EventHandler


class Reflector(object):

    def __init__(self, watch_func):
        super().__init__()
        self.watch_func = watch_func
        self.watcher = None

    def start_watching(self, handlers):
        self.watcher = Thread(target=_watch, args=(self.watch_func, handlers), daemon=True)
        self.watcher.start()


def _watch(func, handlers: List[EventHandler]):
    watch = Watch()
    for e in watch.stream(func):
        obj, event_type = e['object'], e['type']
        for h in handlers:
            if event_type == 'ADDED':
                h.on_add(obj)
            elif event_type == 'MODIFIED':
                h.on_update(obj)
            elif event_type == 'DELETED':
                h.on_delete(obj)
