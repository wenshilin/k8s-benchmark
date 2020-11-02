# names of scheduler configurations
ACTIONS = [
    'DUMMY_SCHEDULER',
    'zb-bit',
    'ls'
]

# identity in pod's label
LABEL_SCHEDULER_NAME = 'linc/schedulerName'

DEFAULT_SCHEDULER_NAME = 'default-scheduler'

TASK_IMAGE = '10.1.114.59:5000/general-task:v7.0'
TASK_TYPES = ['cloud', 'edge1', 'edge2']
TASK_RESOURCE_TYPES = ['cpu', 'memory', 'mix']

KUBE_CONFIG_FILENAME = 'kube-config'

GB = 1024 ** 3
