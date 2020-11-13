import datetime

from kubernetes import client, utils

from .. import consts

GB = 1024 ** 3


def get_obj_uid(obj):
    return obj.metadata.uid


def get_obj_name(obj):
    return obj.metadata.name


def obj_label_equals(obj, label, value):
    return obj.metadata.labels.get(label) == value


def get_pod_node_name(pod: client.V1Pod) -> str:
    return pod.spec.node_name


def get_pod_waiting_time(pod: client.V1Pod) -> float:
    created_at = get_pod_creation_timestamp(pod)
    started_at = get_pod_start_time(pod)
    pod_wait_time = (started_at - created_at).total_seconds()
    if pod_wait_time < 0:
        pod_wait_time = 0.0
    return pod_wait_time


def get_pod_creation_timestamp(pod: client.V1Pod) -> datetime:
    return pod.metadata.creation_timestamp


def get_pod_running_time(pod: client.V1Pod) -> float:
    started_at = get_pod_start_time(pod)
    finished_at = get_pod_finish_time(pod)
    return (finished_at - started_at).total_seconds()


def get_pod_complete_time(pod: client.V1Pod) -> float:
    finished_at = get_pod_finish_time(pod)
    created_at = get_pod_creation_timestamp(pod)
    return (finished_at - created_at).total_seconds()


def get_pod_start_time(pod: client.V1Pod) -> datetime:
    return pod.status.container_statuses[0].state.terminated.started_at


def get_pod_finish_time(pod: client.V1Pod) -> datetime:
    return pod.status.container_statuses[0].state.terminated.finished_at


def get_pod_job_name(pod: client.V1Pod) -> str:
    return pod.metadata.labels['job']


def get_pod_limit_cpu(pod: client.V1Pod) -> str:
    return get_pod_first_container(pod).resources.limits['cpu']


def get_pod_limit_cpu_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_limit_cpu(pod)))


def get_pod_limit_memory(pod: client.V1Pod) -> str:
    return get_pod_first_container(pod).resources.limits['memory']


def get_pod_limit_memory_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_limit_memory(pod))) / GB


def get_pod_request_cpu(pod: client.V1Pod) -> str:
    return get_pod_first_container(pod).resources.requests['cpu']


def get_pod_request_cpu_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_request_cpu(pod)))


def get_pod_request_cpu_float_optional(pod: client.V1Pod) -> float:
    try:
        return get_pod_request_cpu_float(pod)
    except:
        return 0


def get_pod_first_container(pod: client.V1Pod):
    return pod.spec.containers[0]


def get_pod_request_memory(pod: client.V1Pod) -> str:
    return get_pod_first_container(pod).resources.requests['memory']


def get_pod_request_memory_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_request_memory(pod))) / GB


def get_pod_job_id(pod: client.V1Pod) -> str:
    return pod.metadata.labels['job']


def get_pod_workload(pod: client.V1Pod) -> int:
    return int(get_pod_first_container(pod).args[5])


def pod_finished(pod: client.V1Pod):
    return pod_succeeded(pod) or pod_failed(pod)


def pod_succeeded(pod: client.V1Pod):
    return pod.status.phase == 'Succeeded'


def pod_failed(pod: client.V1Pod):
    return pod.status.phase == 'Failed'


def pod_running(pod: client.V1Pod):
    return pod.status.phase == 'Running'


def pod_pending(pod: client.V1Pod):
    return pod.status.phase == 'Pending'


def pod_container_creating(pod: client.V1Pod):
    return pod.status.phase == 'ContainerCreating'


def does_pod_use_resource(pod: client.V1Pod):
    return pod_running(pod) or pod_pending(pod) or pod_container_creating(pod)


def is_workload(pod: client.V1Pod):
    labels = pod.metadata.labels
    return labels is not None and 'app' in labels and labels['app'] == 'linc-workload'


def need_process(pod: client.V1Pod):
    return not assigned_pod(pod) and \
           not assigned_scheduler(pod) and \
           responsible_for_pod(pod, consts.THIS_SCHEDULER_NAME)


def assigned_pod(pod: client.V1Pod):
    return pod.spec.node_name


def assigned_scheduler(pod: client.V1Pod):
    labels = pod.metadata.labels
    return labels is not None and consts.LABEL_SCHEDULER_NAME in labels


def get_pod_resource_type(pod: client.V1Pod):
    return pod.metadata.labels.get('taskType', None)


def get_pod_resource_type_index(pod: client.V1Pod):
    resource_type = get_pod_resource_type(pod)
    return consts.TASK_RESOURCE_TYPES.index(resource_type)


def get_node_requested_cpu(pods):
    sum_cpu = 0
    for p in pods:
        requested_cpu = get_pod_request_cpu_float_optional(p)
        sum_cpu += requested_cpu
    return sum_cpu


def get_node_requested_mem(pods):
    sum_mem = 0
    for p in pods:
        requested_mem = get_pod_request_memory_float(p)
        sum_mem += requested_mem
    return sum_mem


def get_pod_scheduler_name(pod: client.V1Pod):
    return pod.spec.scheduler_name


def responsible_for_pod(pod: client.V1Pod, scheduler_name: str):
    return get_pod_scheduler_name(pod) == scheduler_name


def is_worker_node(node) -> bool:
    return 'linc/nodeType' in node.metadata.labels


def action_valid(action: int):
    return action is not None and action != 0


def convert_action_to_scheduler_name(action: int):
    return consts.ACTIONS[action]
