import math,random

from scipy import stats

from common import consts
from .workload_generator_edge_cloud_edge import WorkloadGenerator


class Edge2Cloud2EdgeWorkloadGenerator(WorkloadGenerator):
    """
    边到云到边负载生成
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:3])
        self.poisson_dist = stats.poisson.rvs(mu=10000, size=1000, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_3 = False
        while len(job_dict['job.tasks']) <= 1:
            job_dict = self._random_choose_job()
            first_3 = True

        if first_3:
            tasks = self._generate_general_tasks(job_dict, 3)
        else:
            tasks = self._generate_general_tasks(job_dict, self.jobconsist_tasknumber)

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])
        for t in tasks:
            #t['startTime'] = t['startTime'] - min_start_time + self.prev_job_last_start_time
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        print('job name: ', ('job-' + str(self.job_count)))
        print('next job start time: ', self.prev_job_last_start_time)
        print('job contains task number: ', len(tasks))
        print('task total number: ', self.task_count)
        print('')
        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]

        return tasks

    def _post_process_tasks(self, tasks):

        for i, task in enumerate(tasks):
            task.job_tasknum = 'n' + str(len(tasks))
            if task.node_type == 'cloud':
                # Mix
                #task.request_mem_mb = task.request_mem_mb
                #task.limit_mem_mb = task.limit_mem_mb
                task.task_type = 'mix'

                #Memory
                #task.request_mem_mb += 3000
                #task.limit_mem_mb += 3000
                #task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))
                #if (task.limit_mem_mb > 7700 or task.memory_mb > 7700 or task.request_mem_mb > 7700):
                #    task.limit_mem_mb = 7700
                #    task.request_mem_mb = 7700
                #    task.memory_mb = 7700
                #task.task_type = 'memory'

            elif task.node_type == 'edge1':
                # Mix
                #task.request_mem_mb = task.request_mem_mb
                #task.limit_mem_mb = task.limit_mem_mb
                task.task_type = 'mix'

                # Memory
                #task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))
                #if (task.limit_mem_mb > 1700 or task.memory_mb > 1700 or task.request_mem_mb > 1700):
                #    task.limit_mem_mb = 1700
                #    task.request_mem_mb = 1700
                #    task.memory_mb = 1700
                #task.task_type = 'memory'

        tasks = self._build_dicts(tasks)
        return tasks
