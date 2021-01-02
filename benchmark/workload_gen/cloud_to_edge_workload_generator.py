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
        #self.poisson_dist = stats.poisson.rvs(mu=75000, size=1000, random_state=1)  #bra
        # self.poisson_dist = stats.poisson.rvs(mu=140000, size=1000, random_state=1)  # mrp
        self.poisson_dist = stats.poisson.rvs(mu=150000, size=1000, random_state=1)  #lrp

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_2 = False
        while len(job_dict['job.tasks']) <= 1:
            job_dict = self._random_choose_job()
            first_2 = True

        if first_2:
            tasks = self._generate_general_tasks(job_dict, 2)
        else:
            tasks = self._generate_general_tasks(job_dict, self.jobconsist_tasknumber)

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])

        for t in tasks:
            #t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)
            t['startTime'] = int(self.prev_job_last_start_time)

        print('job name: ',('job-' + str(self.job_count)))
        print('next job start time: ', self.prev_job_last_start_time)
        print('job contains task number: ',len(tasks))
        print('task total number: ', self.task_count)
        print('')
        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + self.poisson_dist[self.job_count]

        return tasks

    def _post_process_tasks(self, tasks):
        cloud_task_cnt = 0
        edge_task_cnt = 0
        for i, task in enumerate(tasks):
            task.job_tasknum = 'n' + str(len(tasks))
            if task.node_type == 'cloud':
                # CPU
                if cloud_task_cnt % 3 == 0:
                    task.request_cpu = 2
                    task.limit_cpu = 4
                    task.cpu_count = 4
                    task.memory_mb = 10
                    task.limit_mem_mb = 60
                    task.request_mem_mb = 10
                    task.time_ms = int(240000/task.cpu_count)
                    task.task_type = 'cpu'

                elif cloud_task_cnt % 3 == 1:
                    task.request_cpu = 3
                    task.limit_cpu = 4
                    task.cpu_count = 4
                    task.memory_mb = 10
                    task.limit_mem_mb = 60
                    task.request_mem_mb = 10
                    task.time_ms = int(480000/task.cpu_count)
                    task.task_type = 'cpu'

                elif cloud_task_cnt % 3 == 2:
                    task.request_cpu = 3.7
                    task.limit_cpu = 6
                    task.cpu_count = 6
                    task.memory_mb = 10
                    task.limit_mem_mb = 60
                    task.request_mem_mb = 10
                    task.time_ms = int(360000/task.cpu_count)
                    task.task_type = 'cpu'

                cloud_task_cnt += 1

            elif task.node_type == 'edge1':
                # CPU
                if edge_task_cnt % 3 == 0:
                    task.request_cpu = 1
                    task.limit_cpu = 2
                    task.cpu_count = 2
                    task.memory_mb = 5
                    task.limit_mem_mb = 55
                    task.request_mem_mb = 5
                    task.time_ms = int(120000/task.cpu_count)
                    task.task_type = 'cpu'

                elif edge_task_cnt % 3 == 1:
                    task.request_cpu = 1.5
                    task.limit_cpu = 2
                    task.cpu_count = 2
                    task.memory_mb = 5
                    task.limit_mem_mb = 55
                    task.request_mem_mb = 5
                    task.time_ms = int(240000/task.cpu_count)
                    task.task_type = 'cpu'

                elif edge_task_cnt % 3 == 2:
                    task.request_cpu = 1.7
                    task.limit_cpu = 3
                    task.cpu_count = 3
                    task.memory_mb = 5
                    task.limit_mem_mb = 55
                    task.request_mem_mb = 5
                    task.time_ms = int(180000/task.cpu_count)
                    task.task_type = 'cpu'

                edge_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks
