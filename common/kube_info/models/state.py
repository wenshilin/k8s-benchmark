from dataclasses import dataclass
from typing import List

import torch

from .node import NodeState
from .pod import RunPodState, WaitPodState

EMPTY_RUN_POD_STATE = RunPodState('', 0, 0, 0, '')
RUN_POD_STATE_N_FEAT = len(vars(EMPTY_RUN_POD_STATE))
EMPTY_WAIT_POD_STATE = WaitPodState(0, 0, 0, 0, 0, '')
WAIT_POD_STATE_N_FEAT = len(vars(EMPTY_WAIT_POD_STATE))


NODE_STATE_NORMALIZATION_FUNCTIONS = {
    'cpu_usage': lambda value, node, nodes: value / node.cpu_allocatable,
    'cpu_requested': lambda value, node, nodes: value / node.cpu_allocatable,
    'cpu_allocatable': lambda value, node, nodes: value / max(nodes, key=lambda n: n.cpu_allocatable).cpu_allocatable,
    'mem_usage': lambda value, node, nodes: value / node.mem_allocatable,
    'mem_requested': lambda value, node, nodes: value / node.mem_allocatable,
    'mem_allocatable': lambda value, node, nodes: value / max(nodes, key=lambda n: n.mem_allocatable).mem_allocatable,
}

POD_STATE_NORMALIZATION_FUNCTIONS = {
    'cpu_requested': lambda value, pod, pods: value / 4,
    'cpu_limited': lambda value, pod, pods: value / 4,
    'mem_requested': lambda value, pod, pods: value / 2,
    'mem_limited': lambda value, pod, pods: value / 2,
    'workload': lambda value, pod, pods: value / 10000,
    'run_time': lambda value, pod, pods: value / 10000,
    # FIXME: 这仅对当前的环境有效，当前环境中节点的命名方式为k8s${index}-${hostIp}，函数取值为${index}
    'node_name': lambda value, pod, pods: int(value[3]) / 10,
    'job_id': lambda value, pod, pods: int(value.split('-')[-1]) / 30,
}


@dataclass
class State(object):

    # 节点相关状态
    nodes: List[NodeState]

    # 运行中的所有Pod相关状态
    run_pods: List[RunPodState]

    # 等待中的所有Pod相关状态
    wait_pods: List[WaitPodState]

    # 除去等待队列前c个后的等待Pod数量
    backlog_cnt: int

    # Tensor中包含的run_pods数量
    run_pod_cnt_in_tensor: int

    # Tensor中包含的wait_pods数量
    wait_pod_cnt_in_tensor: int

    def to_tensor(self) -> torch.Tensor:
        tensor = []
        # Nodes
        for node in self.nodes:
            for attr_name, value in vars(node).items():
                tensor.append(NODE_STATE_NORMALIZATION_FUNCTIONS[attr_name](value, node, self.nodes))

        # Run pods
        for i, pod in enumerate(self.run_pods):
            if i == self.run_pod_cnt_in_tensor:
                break
            for attr_name, value in vars(pod).items():
                tensor.append(POD_STATE_NORMALIZATION_FUNCTIONS[attr_name](value, pod, self.run_pods))
        zero_num = self.run_pod_cnt_in_tensor - len(self.run_pods)
        tensor.extend([-1] * RUN_POD_STATE_N_FEAT * zero_num)

        # Wait pods
        for i, pod in enumerate(self.wait_pods):
            if i == self.wait_pod_cnt_in_tensor:
                break
            for attr_name, value in vars(pod).items():
                tensor.append(POD_STATE_NORMALIZATION_FUNCTIONS[attr_name](value, pod, self.wait_pods))
        zero_num = self.wait_pod_cnt_in_tensor - len(self.wait_pods)
        tensor.extend([-1] * WAIT_POD_STATE_N_FEAT * zero_num)

        tensor.append(self.backlog_cnt / 20)
        return torch.Tensor(tensor)
