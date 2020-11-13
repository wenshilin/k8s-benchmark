# names of scheduler configurations
ACTIONS = [
    'linc-scheduler-lrp',
    'linc-scheduler-mrp',
    'linc-scheduler-bra',
]

# identity in pod's label
LABEL_SCHEDULER_NAME = 'linc/schedulerName'
THIS_SCHEDULER_NAME = 'linc-scheduler'

DEFAULT_SCHEDULER_NAME = 'default-scheduler'

TASK_IMAGE = '10.1.114.59:5000/general-task:v7.0'
TASK_TYPES = ['cloud', 'edge1', 'edge2']
TASK_RESOURCE_TYPES = ['cpu', 'memory', 'mix']

KUBE_CONFIG_FILENAME = 'kube-config'

GB = 1024 ** 3
