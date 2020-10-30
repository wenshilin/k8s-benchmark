import math

from scipy import stats

from common import consts
from .workload_generator import WorkloadGenerator


class Edge2Cloud2EdgeWorkloadGenerator(WorkloadGenerator):
    """
    边到云到边负载生成
    """

    def __init__(self):
        super().__init__(consts.TASK_TYPES)
        self.poisson_dist = stats.poisson.rvs(mu=3000, size=20, random_state=1)

    def _generate_job(self):
        job_dict = self._random_choose_job()
        first_3 = False
        while len(job_dict['job.tasks']) <= 2:
            job_dict = self._random_choose_job()
            first_3 = True

        if first_3:
            tasks = self._generate_general_tasks(job_dict, 3)
        else:
            tasks = self._generate_general_tasks(job_dict)

        #if self.task_count<=300:
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
        cloud_task_cnt = 0
        edge_task_cnt = 0
        for i, task in enumerate(tasks):
            if task.node_type == 'cloud':
                # CPU
                if cloud_task_cnt % 2 == 0:
                    #task.cpu_count *= 4
                    task.request_cpu *= 6
                    task.limit_cpu *= 6
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 16:
                        task.cpu_count = 16
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.request_mem_mb *= 50
                    task.limit_mem_mb *= 50
                    task.memory_mb = max(int(task.request_mem_mb), int(task.limit_mem_mb*0.9))
                    task.task_type = 'memory'
                cloud_task_cnt += 1

            elif task.node_type == 'edge1' or task.node_type == 'edge2':
                # CPU
                if edge_task_cnt % 2 == 0:
                    #task.cpu_count *= 25
                    task.request_cpu *= 2
                    task.limit_cpu *= 2
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 4:
                        task.cpu_count = 4
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.request_mem_mb *= 12.5
                    task.limit_mem_mb *= 12.5
                    task.memory_mb = max(int(task.request_mem_mb), int(task.limit_mem_mb*0.9))
                    task.task_type = 'memory'
                edge_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks
