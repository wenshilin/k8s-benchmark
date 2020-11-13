from dataclasses import dataclass


@dataclass
class WaitPodState(object):
    # 请求的CPU使用量
    cpu_requested: float

    # 限制的CPU使用量
    cpu_limited: float

    # 请求的内存使用量
    mem_requested: float

    # 限制的内存使用量
    mem_limited: float

    # 工作量
    workload: int

    # 所属Job ID
    job_id: str


@dataclass
class RunPodState(object):

    # 运行的节点名称
    node_name: str

    # 限制的CPU使用量
    cpu_limited: float

    # 至当前运行的时间
    run_time: int

    # 工作量
    workload: int

    # 所属Job ID
    job_id: str
