from common.utils.json_client import JsonClient


class MetricsServerClient(object):

    def __init__(self, base_url: str):
        self.client = JsonClient(base_url)

    def list_nodes(self):
        return self.client.get_json('nodes')

    def list_node(self, node_name: str):
        return self.client.get_json('nodes/%s' % node_name)

    def list_pods(self):
        return self.client.get_json('pods')

    def list_pod(self, name, namespace='default'):
        return self.client.get_json('namespaces/%s/pods/%s' % (namespace, name))
