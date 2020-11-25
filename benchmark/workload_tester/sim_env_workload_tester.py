import datetime
import logging
import os
from typing import List

import munch
from dateutil import tz
from torch.utils.tensorboard import SummaryWriter

from common import consts
from common.kube_info.jct_caculation import calculate_job_complete_times
from common.kube_info.reward_builder import RewardBuilder
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import now_str
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
        self.last_clock = None

    def run_tests(self, tests):
        workload_dir = os.path.join(self.workload_load_directory, self.workload_generated_time)

        for idx, name in enumerate(tests):
            logging.info("-----------------------------------------------------------------")
            filename = os.path.join(workload_dir, '%s.yaml' % (name,))
            # 后端要求发送字符串，因此不做json解析
            with open(filename, 'r') as f:
                jobs = f.read()
            logging.info('Running %s' % name)
            save_dir = f'results/tensorboard/{now_str()}-sim'

            os.makedirs(save_dir, exist_ok=True)
            summary_writer = SummaryWriter(save_dir)

            self.action = algorithm_to_index(name) + 1
            logging.info(f'current action index {self.action}')
            self.reward_builder.reset()
            self.start(jobs)
            pods, nodes = self.wait_until_all_job_done(summary_writer, idx)
            self.write_summary(name, pods, nodes)

    def wait_until_all_job_done(self, summary_writer, test_idx):
        done = False
        sum_reward = 0
        pods, nodes = None, None
        t = 0

        while True:
            if done:
                break
            data = self.client.get_json('/step', json={
                'action': self.action
            })
            logging.debug(data)
            done = data['done']
            pods = data['pods']
            pods = munch.munchify(pods)
            current_clock = read_clock(data)
            logging.info(f'current clock {current_clock}')

            finished_pods = self.finished_pods(pods, self.last_clock, current_clock)
            reward = self._get_reward(finished_pods, pods)
            summary_writer.add_scalar('reward', reward, t)
            sum_reward += reward
            t += 1
            self.last_clock = current_clock

        summary_writer.add_scalar('sum_reward', sum_reward, test_idx)
        logging.info(f'simulation finished at time step {t}')
        return pods, nodes

    def _get_reward(self, pods_finished_at_this_timestamp, all_pods) -> float:
        self.reward_builder.pods_finished(pods_finished_at_this_timestamp)
        jct_list = calculate_job_complete_times(pods_finished_at_this_timestamp, all_pods)
        self.reward_builder.jobs_finished(jct_list)
        return self.reward_builder.reward

    @staticmethod
    def finished_pods(pods, last_clock, current_clock):
        return list(filter(lambda p: utils.is_workload(p) and
                           utils.pod_finished(p) and
                           last_clock < utils.get_pod_finish_time(p) <= current_clock, pods))

    def start(self, workload):
        data = self.client.get_json('/reset', json={
            'workload': workload
        })
        logging.debug(data)
        self.last_clock = read_clock(data)

    def write_summary(self, name, pods, nodes):
        now = now_str()
        self.summarizer.write_summary(pods, now, name, nodes)


def algorithm_to_index(name: str):
    for idx, action in enumerate(consts.SCHEDULING_ALGORITHMS):
        if name.split('-')[-1] in action:
            return idx
    raise RuntimeError(f'{name} not found')


def read_clock(data):
    clock_str = data['clock']
    return datetime.datetime.strptime(clock_str, '%Y-%m-%dT%H:%M:%S%z').astimezone(tz.tzutc()).replace(tzinfo=None)
