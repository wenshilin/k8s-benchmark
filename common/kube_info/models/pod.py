from dataclasses import dataclass


@dataclass
class Pod(object):
    cpu_request: float = None
    cpu_limit: float = None

    mem_request: float = None
    mem_limit: float = None
    type_pod: int = None
