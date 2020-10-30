# names of scheduler configurations
ACTIONS = [
    'DUMMY_SCHEDULER',
    'linc-scheduler-configuration-1',
    'linc-scheduler-configuration-2',
    'linc-scheduler-configuration-3',
    'aladdin-scheduler',
]

# identity in pod's label
LABEL_SCHEDULER_NAME = 'linc/schedulerName'

DEFAULT_SCHEDULER_NAME = 'default-scheduler'

TASK_IMAGE = '10.1.114.59:5000/general-task:v7.0'
TASK_TYPES = ['cloud', 'edge1', 'edge2']
TASK_RESOURCE_TYPES = ['cpu', 'disk']

KUBE_CONFIG_FILENAME = 'kube-config'

GB = 1024 ** 3
