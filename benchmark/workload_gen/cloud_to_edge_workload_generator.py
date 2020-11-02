import math
import random

from scipy import stats

from common import consts
from .workload_generator_cloud_edge import WorkloadGenerator


class Cloud2EdgeWorkloadGenerator(WorkloadGenerator):
    """
    云到边负载生成器
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:2])
        self.poisson_dist = stats.poisson.rvs(mu=8000, size=20, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_2 = False
        while len(job_dict['job.tasks']) <= 1:
            job_dict = self._random_choose_job()
            first_2 = True

        if first_2:
            tasks = self._generate_general_tasks(job_dict, 2)
        else:
            tasks = self._generate_general_tasks(job_dict, random.randint(6,15))

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])

        for t in tasks:
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]
        print('job start time: ', self.prev_job_last_start_time)
        return tasks

    def _post_process_tasks(self, tasks):
        for i, task in enumerate(tasks):
            if task.node_type == 'cloud':
                # CPU
                task.request_cpu += 3
                task.limit_cpu += 4
                task.cpu_count = max(math.ceil(task.request_cpu), math.ceil(task.limit_cpu))
                if task.cpu_count > 8 or task.limit_cpu > 8 or task.request_cpu > 8:
                    task.cpu_count = 8
                    task.limit_cpu = 8
                    task.request_cpu = 7
                task.task_type = 'cpu'

            elif task.node_type == 'edge1':
                # CPU
                task.request_cpu += 1
                task.limit_cpu += 2
                task.cpu_count = max(math.ceil(task.request_cpu), math.ceil(task.limit_cpu))
                if task.cpu_count > 2 or task.limit_cpu > 2 or task.request_cpu > 2:
                    task.cpu_count = 2
                    task.limit_cpu = 2
                    task.request_cpu = 1
                task.task_type = 'cpu'

        tasks = self._build_dicts(tasks)
        return tasks
