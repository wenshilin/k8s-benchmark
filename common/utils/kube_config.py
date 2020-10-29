import kubernetes

from common import consts


def load_kube_config():
    kubernetes.config.kube_config.load_kube_config(config_file=consts.KUBE_CONFIG_FILENAME)
