import dataclasses

from common import consts


@dataclasses.dataclass
class Task(object):
    start_ms: int = 0
    end_ms: int = 0

    cpu_count: int = 0
    memory_mb: int = 0
    time_ms: int = 0
    server_url: str = 'http://localhost:80'
    send_size_mb: int = 0
    write_size_mb: int = 0

    request_cpu: float = 1
    limit_cpu: float = 1
    request_mem_mb: float = 10
    limit_mem_mb: float = 10

    name: str = None
    job_name: str = None
    job_tasknum: str = None
    task_type: str = None
    node_type: str = None
    scheduler_name: str = None
    container_image: str = consts.TASK_IMAGE
