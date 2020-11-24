import math,random

from scipy import stats

from common import consts
from .workload_generator_edge_cloud_edge import WorkloadGenerator


class Edge2Cloud2EdgeWorkloadGenerator(WorkloadGenerator):
    """
    边到云到边负载生成
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES)
        self.poisson_dist = stats.poisson.rvs(mu=8000, size=20, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_2 = False
        while len(job_dict['job.tasks']) <= 2:
            job_dict = self._random_choose_job()
            first_2 = True

        if first_2:
            tasks = self._generate_general_tasks(job_dict, 3)
        else:
            tasks = self._generate_general_tasks(job_dict, random.randint(6,15))

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])
        for t in tasks:
            #t['startTime'] = t['startTime'] - min_start_time + self.prev_job_last_start_time
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]
        print('job start time: ', self.prev_job_last_start_time)
        return tasks

    def _post_process_tasks(self, tasks):

        for i, task in enumerate(tasks):
            if task.node_type == 'cloud':
                # Mix
                task.request_mem_mb = task.request_mem_mb
                task.limit_mem_mb = task.limit_mem_mb
                task.task_type = 'mix'

            elif task.node_type == 'edge1' or task.node_type == 'edge2':
                # Mix
                task.request_mem_mb = task.request_mem_mb
                task.limit_mem_mb = task.limit_mem_mb
                task.task_type = 'mix'

        tasks = self._build_dicts(tasks)
        return tasks