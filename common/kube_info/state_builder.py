from typing import List

import kubernetes
from kubernetes.client import V1Pod, V1Node

from common.consts import GB
from common.kube_info.models.state import State, NodeState, RunPodState, WaitPodState
from common.utils import kube as utils


class StateBuilder(object):

    def __init__(self, pod_cache, kube_client, metrics_server, summary_writer, run_pod_cnt: int, wait_pod_cnt: int):
        self.cache = pod_cache
        self.client = kube_client
        self.metrics_server = metrics_server
        self.summary_writer = summary_writer
        self.run_pod_cnt = run_pod_cnt
        self.wait_pod_cnt = wait_pod_cnt
        self.timestep = 0

    def build(self, has_pod: bool = False):
        self.timestep += 1
        nodes = self._build_node_state()
        run_pods = self._build_run_pod_state()
        wait_pods = self._build_wait_pods_state()
        backlog_cnt = self._get_wait_count(wait_pods, has_pod)
        return State(nodes, run_pods, wait_pods, backlog_cnt, self.run_pod_cnt, self.wait_pod_cnt)

    def _build_node_state(self) -> List[NodeState]:
        states = []
        nodes = self.client.list_node().items
        # sort by node name
        nodes.sort(key=lambda n: utils.get_obj_name(n))

        for node in nodes:
            # This node is not a worker, should be skipped
            if not utils.is_worker_node(node):
                continue

            node_name = utils.get_obj_name(node)
            metrics = self.metrics_server.list_node(node_name)
            pods_run_at_this_node = self._get_pods_run_at_node(node_name)
            state = node_to_node_state(node, metrics, pods_run_at_this_node)
            states.append(state)

            if self.summary_writer:
                self.summary_writer.add_scalar(
                    f'nodes/cpu_utilization/{node_name}', state.cpu_usage / state.cpu_allocatable, self.timestep)
                self.summary_writer.add_scalar(
                    f'nodes/memory_utilization/{node_name}', state.mem_usage / state.mem_allocatable, self.timestep)
                self.summary_writer.add_scalar(
                    f'nodes/requested_cpu/{node_name}', state.cpu_requested / state.cpu_allocatable, self.timestep)

        return states

    def _build_wait_pods_state(self) -> List[WaitPodState]:
        pods = self.cache.filter(utils.need_process)
        # sort by creation timestamp
        pods.sort(key=utils.get_pod_creation_timestamp)

        states = []
        for p in pods:
            run_pod = pod_to_wait_pod_state(p)
            states.append(run_pod)

        return states

    def _build_run_pod_state(self) -> List[RunPodState]:
        pods = self._get_running_pods()
        # sort by creation timestamp
        pods.sort(key=utils.get_pod_creation_timestamp)

        states = []
        for p in pods:
            run_pod = pod_to_run_pod_state(p)
            states.append(run_pod)

        return states

    def _get_pods_run_at_node(self, node_name):
        return self.cache.filter(lambda p: utils.get_pod_node_name(p) == node_name and
                                 utils.is_workload(p) and utils.does_pod_use_resource(p))

    # FIXME: running pods should not only contain Running Pods, but also contain ContainerCreating Pods
    def _get_running_pods(self):
        return self.cache.filter(lambda p: utils.is_workload(p) and utils.pod_running(p))

    def _get_wait_count(self, wait_pods, has_pod):
        wait_count = len(wait_pods)
        if has_pod:
            wait_count += 1
        return max(0, wait_count - self.wait_pod_cnt)


def pod_to_run_pod_state(pod: V1Pod) -> RunPodState:
    cpu_limited = utils.get_pod_limit_cpu_float(pod)
    node_name = utils.get_pod_node_name(pod)
    workload = utils.get_pod_workload(pod)
    job_id = utils.get_pod_job_id(pod)
    return RunPodState(node_name, cpu_limited, 0, workload, job_id)


def pod_to_wait_pod_state(pod: V1Pod) -> WaitPodState:
    limit_cpu = utils.get_pod_limit_cpu_float(pod)
    request_cpu = utils.get_pod_request_cpu_float(pod)

    limit_mem = utils.get_pod_limit_memory_float(pod)
    request_mem = utils.get_pod_request_memory_float(pod)

    workload = utils.get_pod_workload(pod)
    job_id = utils.get_pod_job_id(pod)
    return WaitPodState(request_cpu, limit_cpu, request_mem, limit_mem, workload, job_id)


def node_to_node_state(node: V1Node, metrics: dict, pods_run_at_this_node) -> NodeState:
    cpu_cap = float(kubernetes.utils.parse_quantity(node.status.allocatable['cpu']))
    mem_cap = float(kubernetes.utils.parse_quantity(node.status.allocatable['memory'])) / GB

    cpu_usage = float(kubernetes.utils.parse_quantity(metrics['usage']['cpu']))
    mem_usage = float(kubernetes.utils.parse_quantity(metrics['usage']['memory'])) / GB

    requested_cpu = utils.get_node_requested_cpu(pods_run_at_this_node)
    requested_mem = utils.get_node_requested_mem(pods_run_at_this_node)

    return NodeState(cpu_usage, requested_cpu, cpu_cap,
                     mem_usage, requested_mem, mem_cap)
