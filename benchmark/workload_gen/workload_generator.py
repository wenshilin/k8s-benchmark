import random
import typing

import yaml
import math

from common import consts
from common.utils.json import read_sql_file
from .task import Task


class WorkloadGenerator(object):

    def __init__(self, task_types: list):
        # set some parameters
        self.job_number = 14
        self.tracetimeid = 1
        self.workloadtypeid = 4
        self.jobconsist_tasknumber = 4
        self.job_tasknum = 10000

        self.trace_data = read_sql_file(self.tracetimeid, self.workloadtypeid, self.jobconsist_tasknumber,self.job_tasknum)
        self.job_count = 0
        self.task_count = 0
        self.task_types = task_types
        self.prev_job_last_start_time = 0

    def _random_choose_job(self):
        return random.choice(self.trace_data)

    def _task_type(self):
        return random.choice(self.task_types)

    def _get_task_parameters(self, task: dict):
        start_ms = task[5]
        end_ms = task[6]
        cpu = task[10]
        max_cpu = task[11]
        ram = task[12]
        max_ram = task[13]
        return self._process_task_parameters(start_ms, end_ms, cpu, max_cpu, ram, max_ram)

    @staticmethod
    def _process_task_parameters(start_ms, end_ms, cpu, max_cpu, ram, max_ram, io):
        params = {
            'start_ms': start_ms,
            'end_ms': end_ms,
            'cpu_count': max(1, math.ceil(max_cpu/100)),
            'memory_mb': int(ram * 1024),
            'time_ms': int((end_ms - start_ms) * 1000),
            'request_cpu': float(cpu/100),
            'limit_cpu': float(max_cpu/100),
            'request_mem_mb': int(ram * 1024),
            'limit_mem_mb': int(max_ram * 1024),
        }
        return Task(**params)

    def _job_num(self):
        return len(self.trace_data)

    def _generate_job(self) -> list:
        pass

    def generate(self):
        jobs = []
        job_num = self._job_num()
        for _ in range(job_num):
            if self.job_count <= self.job_number:
                print('job count: ',self.job_count)
                job = self._generate_job()
                jobs.append(job)
                self.job_count += 1
        return jobs

    def _generate_general_tasks(self, job_dict: dict, first_n: int = 100) -> list:
        task_dict = job_dict['job.tasks']
        tasks = []

        for i, task in enumerate(task_dict):
            if i == first_n:
                break

            task = self._get_task_parameters(task)
            if i % 3 == 0:
                task_type = 'cloud'
            elif i % 3 == 1:
                task_type = 'edge1'
            elif i % 3 == 2 and len(self.task_types) == 3:
                task_type = 'edge2'

            task.node_type = task_type

            task.job_name = 'job-' + str(self.job_count)
            task.name = task.job_name + '-' + task_type + '-' + str(self.task_count)
            tasks.append(task)
            self.task_count += 1

        return tasks

    def _post_process_tasks(self, tasks: typing.List[Task]) -> typing.List[dict]:
        pass

    def _build_dicts(self, tasks: typing.List[Task]) -> typing.List[dict]:
        for i, task in enumerate(tasks):
            # To solve OOMKilled
            need_mem_mb = task.write_size_mb + task.memory_mb + 150
            task.memory_mb = need_mem_mb
            task.limit_mem_mb = need_mem_mb + 50
            task.request_mem_mb = need_mem_mb

            # Reduces working time
            task.time_ms *= (task.limit_cpu + 1)
            while task.time_ms >= 300000:
                task.time_ms = int(task.time_ms / 2)
            if task.limit_cpu < 1:
                task.time_ms *= (task.limit_cpu + 1)

            # Build dictionary
            tasks[i] = build_task_dict(task)

        return tasks


with open('templates/task-template.yaml') as f:
    WORKLOAD_POD_TEMPLATE = f.read()


def build_task_dict(task: Task):
    if task.node_type not in consts.TASK_TYPES:
        raise RuntimeError('The type %s of workload is supported.' % task.node_type)

    scheduler_name = task.scheduler_name
    if not scheduler_name:
        scheduler_name = consts.DEFAULT_SCHEDULER_NAME

    s = WORKLOAD_POD_TEMPLATE \
        .replace('$NAME', task.name) \
        .replace('$JOB_NAME', task.job_name) \
        .replace('$JOB_TASKNUM', task.job_tasknum) \
        .replace('$TASK_TYPE', task.task_type) \
        .replace('$SCHEDULER_NAME', scheduler_name) \
        .replace('$CONTAINER_IMAGE', task.container_image) \
        .replace('$CPU_COUNT', str(task.cpu_count)) \
        .replace('$MEMORY_MB', str(task.memory_mb)) \
        .replace('$ITER_FACTOR', str(int(task.time_ms))) \
        .replace('$NODE_TYPE', task.node_type) \
        .replace('$START_TIME', str(task.start_ms)) \
        .replace('$REQUEST_MEM_MB', str(task.request_mem_mb)) \
        .replace('$REQUEST_CPU', str(round(task.request_cpu, 4))) \
        .replace('$LIMIT_MEM_MB', str(task.limit_mem_mb)) \
        .replace('$LIMIT_CPU', str(round(task.limit_cpu, 4)))

    return yaml.load(s, Loader=yaml.SafeLoader)
