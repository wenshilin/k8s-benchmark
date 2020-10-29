import os
import pickle

from .summary_plugin import SummaryPlugin


class PodSummaryPlugin(SummaryPlugin):
    """
    Pod相关的总结，包含当前集群的Pod信息
    """
    def __init__(self):
        self.save_dir = 'results/pods'
        self.now = ''

    def write_summary(self, pods, now: str, name: str):
        self.now = now
        os.makedirs(self.save_dir, exist_ok=True)
        save_dir = os.path.join(self.save_dir, '%s-%s.pk' % (str(self.now), name))
        with open(save_dir, 'wb') as f:
            pickle.dump(pods, f)
