import math

from scipy import stats

from common import consts
from .workload_generator import WorkloadGenerator


class Cloud2EdgeWorkloadGenerator(WorkloadGenerator):
    """
    云到边负载生成器
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
            tasks = self._generate_general_tasks(job_dict)

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])

        for t in tasks:
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]
        print('job start time: ', self.prev_job_last_start_time)
        return tasks

    def _post_process_tasks(self, tasks):
        cloud_task_cnt = 0
        edge1_task_cnt = 0
        for i, task in enumerate(tasks):
            if task.node_type == 'cloud':
                # CPU
                if cloud_task_cnt % 2 == 0:
                    #task.cpu_count *= 4
                    task.request_cpu = 4
                    task.limit_cpu = 8
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 8:
                        task.cpu_count = 8
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.memory_mb *= 4
                    task.request_mem_mb *= 4
                    task.limit_mem_mb *= 4
                    task.task_type = 'memory'
                cloud_task_cnt += 1

            elif task.node_type == 'edge1':
                # CPU
                if edge1_task_cnt % 2 == 0:
                    #task.cpu_count *= 25
                    task.request_cpu = 1
                    task.limit_cpu = 2
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 2:
                        task.cpu_count = 2
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.memory_mb *= 1
                    task.request_mem_mb *= 1
                    task.limit_mem_mb *= 1
                    task.task_type = 'memory'
                edge1_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks
