import math
import random

from scipy import stats

from common import consts
from .workload_generator_high_cpu_memory import WorkloadGenerator


class HighCpuAndMemoryWorkloadGenerator(WorkloadGenerator):
    """
    高CPU和MEMORY负载生成器
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:2])
        self.poisson_dist = stats.poisson.rvs(mu=150000, size=1000, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_2 = False
        while len(job_dict['job.tasks']) <= 1:
            job_dict = self._random_choose_job()
            first_2 = True

        if first_2:
            tasks = self._generate_general_tasks(job_dict, 2)
        else:
            tasks = self._generate_general_tasks(job_dict,self.jobconsist_tasknumber)

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])

        for t in tasks:
            #t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)
            t['startTime'] = int(self.prev_job_last_start_time)

        print('job name: ', ('job-' + str(self.job_count)))
        print('next job start time: ', self.prev_job_last_start_time)
        print('job contains task number: ', len(tasks))
        print('task total number: ', self.task_count)
        print('')
        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]

        return tasks

    def _post_process_tasks(self, tasks):
        cloud_task_cnt = 0
        edge1_task_cnt = 0
        for i, task in enumerate(tasks):
            task.job_tasknum = 'n' + str(len(tasks))
            if task.node_type == 'cloud':
                if cloud_task_cnt % 2 == 0:
                   # Memory
                   task.request_mem_mb += 2048
                   task.limit_mem_mb += 2548
                   task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))
                   if (task.limit_mem_mb > 3700 or task.memory_mb > 3700 or task.request_mem_mb > 3700):
                       task.limit_mem_mb = 3700
                       task.request_mem_mb = 3700
                       task.memory_mb = 3700

                    # CPU
                   task.request_cpu /= 2
                   task.limit_cpu /= 2
                   task.request_cpu = min(2, task.request_cpu)
                   task.limit_cpu = min(2, task.limit_cpu)
                   task.cpu_count = max(1, math.ceil(task.request_cpu))
                   task.time_ms = int(task.time_ms / 50)

                   task.task_type = 'memory'

                else:
                    # Memory
                    task.request_mem_mb -= 650
                    task.limit_mem_mb -= 650
                    task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))

                    # CPU
                    task.request_cpu *= 2
                    task.limit_cpu *= 2
                    task.limit_cpu = min(4, task.limit_cpu)
                    task.cpu_count = max(1, math.ceil(task.request_cpu))
                    if task.request_cpu > 4:
                        task.cpu_count = 4
                        task.limit_cpu = 4
                        task.request_cpu = 4

                    task.task_type = 'cpu'

                cloud_task_cnt += 1

            elif task.node_type == 'edge1':
                if edge1_task_cnt % 2 == 0:
                    # Memory
                    task.request_mem_mb += 1024
                    task.limit_mem_mb += 1536
                    task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))
                    if (task.limit_mem_mb > 1700 or task.memory_mb > 1700 or task.request_mem_mb > 1700):
                         task.limit_mem_mb = 1700
                         task.request_mem_mb = 1700
                         task.memory_mb = 1700

                    # CPU
                    task.request_cpu /= 4
                    task.limit_cpu /= 4
                    task.request_cpu = min(1, task.request_cpu)
                    task.limit_cpu = min(1, task.limit_cpu)
                    task.cpu_count = max(1, math.ceil(task.request_cpu))
                    task.time_ms = int(task.time_ms / 100)

                    task.task_type = 'memory'

                else:
                    # Memory
                    task.request_mem_mb -= 650
                    task.limit_mem_mb -= 650
                    task.memory_mb = min(int(task.request_mem_mb), int(task.limit_mem_mb))

                    # CPU
                    # task.request_cpu += 1
                    # task.limit_cpu += 2
                    task.limit_cpu = min(2, task.limit_cpu)
                    task.cpu_count = max(1, math.ceil(task.request_cpu))
                    if task.request_cpu > 2:
                        task.cpu_count = 2
                        task.limit_cpu = 2
                        task.request_cpu = 2

                    task.task_type = 'cpu'

                edge1_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks
