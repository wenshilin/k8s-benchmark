import collections


class Cache(object):
    def __init__(self):
        self.objects = collections.OrderedDict()

    def get_all(self):
        return self.objects.values()

    def get(self, key: str):
        return self.objects.get(key, None)

    def filter(self, func):
        return filter(func, self.objects.values())

    def put(self, key, obj):
        self.objects[key] = obj

    def delete(self, key):
        del self.objects[key]
