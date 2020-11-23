import json
import logging
import os
from typing import List

import munch
from torch.utils.tensorboard import SummaryWriter

from common import consts
from common.kube_info.reward_builder import RewardBuilder
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import now_str, load_from_file
from common.utils.json_http_client import JsonHttpClient
from .abstract_workload_tester import AbstractWorkloadTester


class SimEnvWorkloadTester(AbstractWorkloadTester):

    def __init__(self,
                 base_url: str,
                 workload_type: str,
                 workload_generated_time: str,
                 scheduling_algorithms: List[str],
                 repeat_times: int = 1,
                 workload_load_directory: str = 'workloads'):
        super().__init__(workload_type, workload_generated_time,
                         scheduling_algorithms, repeat_times, workload_load_directory)

        self.action = 0
        self.client = JsonHttpClient(base_url)
        self.summarizer = KubeEvaluationSummarizer()
        self.reward_builder = RewardBuilder()

    def run_tests(self, tests):
        workload_dir = os.path.join(self.workload_load_directory, self.workload_generated_time)

        for idx, name in enumerate(tests):
            logging.info("-----------------------------------------------------------------")
            jobs = load_from_file(os.path.join(workload_dir, '%s.yaml' % (name,)))
            logging.info('Running %s' % name)
            logging.info('loaded job number: %d' % len(jobs))
            save_dir = f'results/tensorboard/{now_str()}-sim'
            os.makedirs(save_dir, exist_ok=True)
            summary_writer = SummaryWriter(save_dir)

            self.action = algorithm_to_index(name) + 1
            logging.info(f'current action index {self.action}')
            self.reward_builder.reset()
            self.start(jobs)
            pods = self.wait_until_all_job_done(summary_writer, idx)
            logging.info("----------------------------------------------------------------------")
            self.write_summary(name, pods)

    def wait_until_all_job_done(self, summary_writer, test_idx):
        done = False
        sum_reward = 0
        pods = None
        t = 0

        while True:
            if done:
                break
            data = self.client.get_json('/step', json={
                'action': self.action
            })
            done = data['done']
            pods = data['pods']
            pods = munch.munchify(pods)

            # FIXME: 当前获得的是所有完成的Pod
            finished_pods = self.finished_pods(pods)
            reward = self._get_reward(finished_pods, pods)
            summary_writer.add_scalar('reward', reward, t)
            sum_reward += reward
            t += 1

        summary_writer.add_scalar('sum_reward', sum_reward, test_idx)
        logging.info(f'simulation finished at time step {t}')
        return pods

    def _get_reward(self, pods_finished_at_this_timestamp, all_pods) -> float:
        self.reward_builder.pods_finished(pods_finished_at_this_timestamp)
        jct_list = self._get_job_complete_times(pods_finished_at_this_timestamp, all_pods)
        self.reward_builder.jobs_finished(jct_list)
        return self.reward_builder.reward

    def _get_job_complete_times(self, finished_pods, all_pods):
        job_ids = self._filter_job_ids(finished_pods)
        return self._calculate_job_complete_times(job_ids, all_pods)

    @staticmethod
    def _filter_job_ids(finished_pods):
        job_ids = set()
        for p in finished_pods:
            job_id = utils.get_pod_job_id(p)
            if job_id not in job_ids:
                job_ids.add(job_id)
        return job_ids

    def _calculate_job_complete_times(self, job_ids, all_pods) -> List[float]:
        jct_list = []
        for job_id in job_ids:
            pods = self._job_finished_pods(job_id, all_pods)
            job_task_number = utils.get_job_task_number(pods[0])
            logging.info(f'job {job_id}: task number {job_task_number}, finished task number {len(pods)}')
            if len(pods) == job_task_number:
                jct = self._calculate_jct(pods)
                jct_list.append(jct)
                logging.info(f'JCT of job {job_id} is {jct}s')
        return jct_list

    @staticmethod
    def _job_finished_pods(job_id, pods):
        return list(filter(lambda p: utils.is_workload(p) and
                           utils.get_pod_job_id(p) == job_id and
                           utils.pod_finished(p), pods))

    @staticmethod
    def finished_pods(pods):
        return list(filter(lambda p: utils.is_workload(p) and utils.pod_finished(p), pods))

    @staticmethod
    def _calculate_jct(pods) -> float:
        first_pod_created_at = min(map(utils.get_pod_creation_timestamp, pods))
        last_pod_finished_at = max(map(utils.get_pod_finish_time, pods))
        return (last_pod_finished_at - first_pod_created_at).total_seconds()

    def start(self, workload):
        # 后端要求发送字符串
        self.client.get_json('/reset', json={
            'workload': json.dumps(workload)
        })

    # FIXME: 在最后一个时间片Pod，Node为空
    def write_summary(self, name, pods):
        now = now_str()
        self.summarizer.write_summary(pods, now, name)


def algorithm_to_index(name: str):
    for idx, action in enumerate(consts.SCHEDULING_ALGORITHMS):
        if name.split('-')[-1] in action:
            return idx
    raise RuntimeError(f'{name} not found')
