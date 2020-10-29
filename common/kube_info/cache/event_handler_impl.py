from .event_handler import EventHandler


class EventHandlerImpl(EventHandler):
    def __init__(self, cache, func):
        super().__init__()
        self.cache = cache
        self.func = func

    def on_add(self, obj):
        self.cache.add(obj, self.func)

    def on_delete(self, obj):
        self.cache.delete(obj)

    def on_update(self, obj):
        self.cache.update(obj)
