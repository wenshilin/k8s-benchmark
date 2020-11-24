import datetime
import logging
import os
import time
import unittest
import warnings
from typing import List

import kubernetes
from torch.utils.tensorboard import SummaryWriter

from benchmark import workload_gen
from common import global_arguments
from common.kube_info.cache.pod_cache import create_pod_cache_and_start_listening
from common.kube_info.metrics_server_client import MetricsServerClient
from common.kube_info.reward_builder import RewardBuilder
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import kube_config
from common.workload.workload_runner import WorkloadRunner


class WorkloadTest(unittest.TestCase):

    def setUp(self) -> None:
        kube_config.load_kube_config()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
        )
        global_arguments.init_empty_arguments()
        self.client = kubernetes.client.CoreV1Api()
        self.summarizer = KubeEvaluationSummarizer()

        self.ms = MetricsServerClient('http://localhost:8001/apis/metrics.k8s.io/v1beta1')
        self.workload_runner = WorkloadRunner(self.client, dry_run=False)
        self.reward_builder = RewardBuilder()
        self.cache = create_pod_cache_and_start_listening(self.client, lambda _: True)

        warnings.simplefilter('ignore', ResourceWarning)

    def test_all(self):
        for _ in range(1):
            self.run_once()

    def run_once(self):
        # 负载的类型
        workload_type = '边到云到边'
        # 负载生成时间/负载所在文件夹
        workload_generated_time = '2020-11-23 22-33-19'

        # scheduling_algorithms = ['ep', 'lrp', 'mrp', 'bra', 'rlp']
        scheduling_algorithms = ['lrp']
        tests = ['%s-%s' % (workload_type, scheduling_algorithm, ) for scheduling_algorithm in scheduling_algorithms]

        workload_dir = os.path.join('results/workloads', workload_generated_time)

        for name in tests:
            print("-----------------------------------------------------------------")
            jobs = workload_gen.load_from_file(os.path.join(workload_dir, '%s.yaml' % (name, )))
            print('Running %s' % name)
            print('loaded job number: %d' % len(jobs))
            save_dir = f'results/tensorboard/{self.now_str()}'
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
        jct_list = self._get_job_complete_times(finished_pods)
        self.reward_builder.jobs_finished(jct_list)
        return self.reward_builder.reward

    def _get_job_complete_times(self, finished_pods):
        job_ids = self._filter_job_ids(finished_pods)
        return self._calculate_job_complete_times(job_ids)

    def _filter_job_ids(self, finished_pods):
        job_ids = set()
        for p in finished_pods:
            job_id = utils.get_pod_job_id(p)
            if job_id not in job_ids:
                job_ids.add(job_id)
        return job_ids

    def _calculate_job_complete_times(self, job_ids) -> List[float]:
        jct_list = []
        for job_id in job_ids:
            pods = self._job_finished_pods(job_id)
            job_task_number = utils.get_job_task_number(pods[0])
            logging.info(f'job {job_id}: task number {job_task_number}, finished task number {len(pods)}')
            if len(pods) == job_task_number:
                jct = self._calculate_jct(pods)
                jct_list.append(jct)
                logging.info(f'JCT of job {job_id} is {jct}s')
        return jct_list

    def _job_finished_pods(self, job_id):
        return self.cache.filter(lambda p: utils.is_workload(p) and
                                 utils.get_pod_job_id(p) == job_id and
                                 utils.pod_finished(p))

    @staticmethod
    def _calculate_jct(pods) -> float:
        first_pod_created_at = min(map(utils.get_pod_creation_timestamp, pods))
        last_pod_finished_at = max(map(utils.get_pod_finish_time, pods))
        return (last_pod_finished_at - first_pod_created_at).total_seconds()

    def start(self, workload):
        self.workload_runner.restart(workload)

    def write_summary(self, name, pods):
        self.now = self.now_str()
        self.summarizer.write_summary(pods, self.now, name)

    def now_str(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')


if __name__ == '__main__':
    unittest.main()
