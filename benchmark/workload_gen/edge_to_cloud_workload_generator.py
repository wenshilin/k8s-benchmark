import math
import random

from scipy import stats

from common import consts
from .workload_generator_edge_cloud import WorkloadGenerator


class Edge2CloudWorkloadGenerator(WorkloadGenerator):
    """
    边到云负载生成
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:2])
        self.poisson_dist = stats.poisson.rvs(mu=5000, size=20, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_2 = False
        while len(job_dict['job.tasks']) <= 1:
            job_dict = self._random_choose_job()
            first_2 = True

        if first_2:
            tasks = self._generate_general_tasks(job_dict, 2)
        else:
            tasks = self._generate_general_tasks(job_dict, 12)

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])
        for i,t in enumerate(tasks):
            #t['startTime'] = t['startTime'] - min_start_time + self.prev_job_last_start_time
            #if i == 0:
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)
            #else:
            #   t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.poisson_dist1[i] + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]
        print('next job start time: ',self.prev_job_last_start_time)
        return tasks

    def _post_process_tasks(self, tasks):

        for i, task in enumerate(tasks):
            task.job_tasknum = 'n' + str(len(tasks))
            if task.node_type == 'cloud':
                # mix
                task.task_type = 'mix'

            elif task.node_type == 'edge1':
                # mix
                task.task_type = 'mix'

        tasks = self._build_dicts(tasks)
        return tasks
