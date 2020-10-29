from typing import *
import kubernetes

from .models.node import Node
from . import utils
from ..consts import GB


class KubeInformer(object):

    def __init__(self, metrics_server, kube_client, pod_cache):
        self.ms = metrics_server
        self.client = kube_client
        self.cache = pod_cache

    def get_nodes(self) -> List[Node]:
        pods = self.client.list_pod_for_all_namespaces()
        pod_cnt = Counter(map(lambda p: p.spec.node_name, pods.items))

        nodes = []
        for n in self.client.list_node().items:
            node_name = n.metadata.name
            if node_name == 'linc':
                continue

            cpu_cap = float(kubernetes.utils.parse_quantity(n.status.allocatable['cpu']))
            mem_cap = float(kubernetes.utils.parse_quantity(n.status.allocatable['memory'])) / GB
            max_pod = int(n.status.allocatable['pods'])

            m = self.ms.list_node(node_name)
            cpu_usage = float(kubernetes.utils.parse_quantity(m['usage']['cpu']))
            mem_usage = float(kubernetes.utils.parse_quantity(m['usage']['memory'])) / GB
            pod_num = pod_cnt[node_name]

            num_cpu_pod = len(
                self.cache.filter(lambda pod: utils.get_pod_node_name(pod) == node_name and utils.get_pod_resource_type(pod) == 'cpu' and not utils.pod_finished(pod))
            )
            num_disk_pod = len(
                self.cache.filter(lambda pod: utils.get_pod_node_name(pod) == node_name and utils.get_pod_resource_type(pod) == 'disk' and not utils.pod_finished(pod))
            )

            pods = self.cache.filter(lambda p: utils.get_pod_node_name(p) == node_name and utils.pod_use_resource(p))
            requested_cpu = utils.get_node_requested_cpu(pods)

            node = Node(node_name, cpu_cap, mem_cap, max_pod,
                        cpu_usage, mem_usage, pod_num, num_cpu_pod, num_disk_pod, requested_cpu)
            nodes.append(node)

        return nodes
