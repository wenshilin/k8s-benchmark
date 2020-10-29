from .event_handler import EventHandler
from .reflector import Reflector


class Informer(object):

    def __init__(self, func):
        self.reflector = Reflector(func)
        self.handlers = []
        self.started = False

    def add_event_handler(self, handler: EventHandler):
        self.handlers.append(handler)

    def run(self):
        if not self.started:
            self.reflector.start_watching(self.handlers)
            self.started = True
