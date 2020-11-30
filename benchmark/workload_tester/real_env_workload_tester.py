import logging
import os
import time
from typing import List

import kubernetes

try:
    from tensorboardX import SummaryWriter
except ImportError:
    from torch.utils.tensorboard import SummaryWriter

from common.kube_info.cache.pod_cache import create_pod_cache_and_start_listening
from common.kube_info.jct_caculation import calculate_job_complete_times
from common.kube_info.metrics_server_client import MetricsServerClient
from common.kube_info.reward_builder import RewardBuilder
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import now_str, load_from_file
from common.workload.workload_runner import WorkloadRunner
from common.kube_info.real_kube_informer import RealKubeInformer
from .abstract_workload_tester import AbstractWorkloadTester


class RealEnvWorkloadTester(AbstractWorkloadTester):

    def __init__(self,
                 metrics_server_base_url: str,
                 workload_type: str,
                 workload_generated_time: str,
                 scheduling_algorithms: List[str],
                 repeat_times: int = 1,
                 workload_load_directory: str = 'workloads'):
        super().__init__(workload_type, workload_generated_time,
                         scheduling_algorithms, repeat_times, workload_load_directory)

        client = kubernetes.client.CoreV1Api()
        metrics_server = MetricsServerClient(metrics_server_base_url)
        cache = create_pod_cache_and_start_listening(client, lambda _: True)
        self.informer = RealKubeInformer(
            pod_cache=cache,
            kube_client=client,
            metrics_server=metrics_server
        )
        self.summarizer = KubeEvaluationSummarizer(self.informer)

        self.workload_runner = WorkloadRunner(client, dry_run=False)
        self.reward_builder = RewardBuilder()

    def run_tests(self, tests):
        workload_dir = os.path.join(self.workload_load_directory, self.workload_generated_time)

        for name in tests:
            logging.info("-----------------------------------------------------------------")
            jobs = load_from_file(os.path.join(workload_dir, '%s.yaml' % (name,)))
            logging.info('Running %s' % name)
            logging.info('loaded job number: %d' % len(jobs))
            save_dir = f'results/tensorboard/{now_str()}-real'
            os.makedirs(save_dir, exist_ok=True)
            summary_writer = SummaryWriter(save_dir)
            self.reward_builder.reset()
            self.start(jobs)
            self.wait_until_all_job_done(summary_writer)
            self.summarizer.write_summary(name)

    def wait_until_all_job_done(self, summary_writer):
        all_pod_finished = False
        t = 0
        sum_reward = 0
        while not all_pod_finished or not self.workload_runner.has_done():
            t += 1
            reward = self._get_reward()
            sum_reward += reward
            summary_writer.add_scalar('reward', reward, t)
            time.sleep(10)
            pods = self.informer.get_node_objects()
            all_pod_finished = all(map(utils.pod_finished, pods))

        summary_writer.add_scalar('sum_reward', sum_reward, 0)

    def _get_reward(self) -> float:
        finished_pods = self.informer.get_finished_pods()
        self.reward_builder.pods_finished(finished_pods)
        all_pods = self.informer.get_pods_objects()
        jct_list = calculate_job_complete_times(finished_pods, all_pods)
        self.reward_builder.jobs_finished(jct_list)
        return self.reward_builder.reward

    def start(self, workload):
        self.workload_runner.restart(workload)
