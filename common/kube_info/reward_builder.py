import logging

from common.utils import kube as utils


class RewardBuilder(object):

    BASE_REWARD = 0

    def __init__(self):
        self._reward: int = 0
        self._finished_pod_cnt = 0
        self.reset()

    def pods_finished(self, finished_pods):
        pod_cnt = 0
        for pod in finished_pods:
            reward = self._single_pod_finished_reward(pod)
            self._reward += reward
            pod_cnt += 1
        logging.info(f"there are {pod_cnt} pods finished in this timestep")
        self._finished_pod_cnt += pod_cnt
        logging.info(f"finished pod count: {self._finished_pod_cnt}")

    def jobs_finished(self, job_complete_times):
        for jct in job_complete_times:
            reward = -0.02 * jct + 20
            logging.info(f"JCT reward: {reward}")
            self._reward += reward

    def backlog(self, pod_cnt: int, time_step_interval: float):
        self._reward -= pod_cnt * 0.002 * time_step_interval

    def reset(self):
        self._reward = RewardBuilder.BASE_REWARD
        self._finished_pod_cnt = 0

    @property
    def reward(self):
        return self._reward

    @staticmethod
    def _single_pod_finished_reward(pod):
        complete_time = utils.get_pod_complete_time(pod)
        reward = -0.002 * complete_time + 2
        logging.info(f'reward for {utils.get_obj_name(pod)}: {reward}, complete time {complete_time}s')
        return reward
