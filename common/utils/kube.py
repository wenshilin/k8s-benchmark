from datetime import datetime

from kubernetes import client, utils

from common import consts

GB = 1024 ** 3


def get_obj_uid(obj):
    return obj.metadata.uid


def get_obj_name(obj):
    return obj.metadata.name


def obj_label_equals(obj, label, value):
    return obj.metadata.labels.get(label) == value


def get_pod_node_name(pod: client.V1Pod):
    return pod.spec.node_name


def get_pod_waiting_time(pod: client.V1Pod) -> float:
    #created_at: datetime = get_pod_creation_timestamp(pod)
    #created_at: datetime = pod.metadata.creation_timestamp
    created_at: datetime = pod.status.start_time
    started_at: datetime = pod.status.container_statuses[0].state.terminated.started_at
    pod_waitingtime = (started_at - created_at).total_seconds()
    #if pod_waitingtime < 0:
    #    pod_waitingtime = 0.0
    return pod_waitingtime


def get_pod_creation_timestamp(pod: client.V1Pod) -> datetime:
    return pod.metadata.creation_timestamp


def get_pod_running_time(pod: client.V1Pod, finished_at: datetime) -> float:
    started_at: datetime = pod.status.start_time
    return (finished_at - started_at).total_seconds()


def get_pod_finish_time(pod: client.V1Pod) -> datetime:
    return pod.status.container_statuses[0].state.terminated.finished_at


def get_pod_job_name(pod: client.V1Pod) -> str:
    return pod.metadata.labels['job']


def get_pod_limit_cpu(pod: client.V1Pod) -> str:
    return pod.spec.containers[0].resources.limits['cpu']


def get_pod_limit_cpu_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_limit_cpu(pod)))


def get_pod_limit_memory(pod: client.V1Pod) -> str:
    return pod.spec.containers[0].resources.limits['memory']


def get_pod_limit_memory_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_limit_memory(pod))) / GB


def get_pod_request_cpu(pod: client.V1Pod) -> str:
    return pod.spec.containers[0].resources.requests['cpu']


def get_pod_request_cpu_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_request_cpu(pod)))


def get_pod_request_cpu_float_optional(pod: client.V1Pod) -> float:
    try:
        return get_pod_request_cpu_float(pod)
    except:
        return 0


def get_pod_request_memory(pod: client.V1Pod) -> str:
    return pod.spec.containers[0].resources.requests['memory']


def get_pod_request_memory_float(pod: client.V1Pod) -> float:
    return float(utils.parse_quantity(get_pod_request_memory(pod))) / GB


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


def pod_use_resource(pod: client.V1Pod):
    return pod_running(pod) or pod_pending(pod) or pod_container_creating(pod)


def is_our_pod(pod: client.V1Pod):
    labels = pod.metadata.labels
    return labels is not None and 'app' in labels and labels['app'] == 'linc-workload'


def need_process(pod: client.V1Pod, scheduler_name):
    return not assigned_pod(pod) and not assigned_scheduler(pod) and responsible_for_pod(pod, scheduler_name)


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


def get_pod_scheduler_name(pod: client.V1Pod):
    return pod.spec.scheduler_name


def responsible_for_pod(pod: client.V1Pod, scheduler_name: str):
    return get_pod_scheduler_name(pod) == scheduler_name


def action_valid(action: int):
    return action is not None and action != 0
