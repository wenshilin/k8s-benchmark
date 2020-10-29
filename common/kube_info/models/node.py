from dataclasses import dataclass


@dataclass
class Node(object):

    node_name: str

    allocatable_cpu: float = None
    allocatable_mem: float = None
    allocatable_pod: int = None

    cpu_usage: float = None
    mem_usage: float = None
    pod_usage: int = None

    num_cpu_pod: int = 0
    num_disk_pod: int = 0

    requested_cpu: float = 0
