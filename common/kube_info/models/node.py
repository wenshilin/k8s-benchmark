from dataclasses import dataclass


@dataclass
class NodeState(object):

    # CPU使用量
    cpu_usage: float

    # 请求的总CPU
    cpu_requested: float

    # 总计可分配的CPU
    cpu_allocatable: float

    # 内存使用量
    mem_usage: float

    # 请求的总内存
    mem_requested: float

    # 总计可分配的内存
    mem_allocatable: float
