import os
import time
from typing import List

import kubernetes
from torch.utils.tensorboard import SummaryWriter

from common.kube_info.cache.pod_cache import create_pod_cache_and_start_listening
from common.kube_info.jct_caculation import calculate_job_complete_times
from common.kube_info.metrics_server_client import MetricsServerClient
from common.kube_info.reward_builder import RewardBuilder
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import now_str, load_from_file
from common.workload.workload_runner import WorkloadRunner
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

        self.client = kubernetes.client.CoreV1Api()
        self.summarizer = KubeEvaluationSummarizer()

        self.ms = MetricsServerClient(metrics_server_base_url)
        self.workload_runner = WorkloadRunner(self.client, dry_run=False)
        self.reward_builder = RewardBuilder()
        self.cache = create_pod_cache_and_start_listening(self.client, lambda _: True)

    def run_tests(self, tests):
        workload_dir = os.path.join(self.workload_load_directory, self.workload_generated_time)

        for name in tests:
            print("-----------------------------------------------------------------")
            jobs = load_from_file(os.path.join(workload_dir, '%s.yaml' % (name,)))
            print('Running %s' % name)
            print('loaded job number: %d' % len(jobs))
            save_dir = f'results/tensorboard/{now_str()}-real'
            os.makedirs(save_dir, exist_ok=True)
            summary_writer = SummaryWriter(save_dir)
            self.reward_builder.reset()
            self.start(jobs)
            self.wait_until_all_job_done(summary_writer)
            pods = self.get_pods()
            self.write_summary(name, pods)

    def get_pods(self):
        return self.client.list_namespaced_pod('default').items

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
            pods = self.get_pods()
            all_pod_finished = all(map(utils.pod_finished, pods))

        summary_writer.add_scalar('sum_reward', sum_reward, 0)
        print('all job finished!!!')
        print("----------------------------------------------------------------------")

    def _get_reward(self) -> float:
        finished_pods = self.cache.get_finished_pods_and_clean_cache()
        self.reward_builder.pods_finished(finished_pods)
        all_pods = self.cache.get_all()
        jct_list = calculate_job_complete_times(finished_pods, all_pods)
        self.reward_builder.jobs_finished(jct_list)
        return self.reward_builder.reward

    def start(self, workload):
        self.workload_runner.restart(workload)

    def write_summary(self, name, pods):
        now = now_str()
        self.summarizer.write_summary(pods, now, name)