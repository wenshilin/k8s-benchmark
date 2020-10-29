# -*- coding: utf-8 -*-

import json
import yaml
import random
import dataclasses
import typing
import logging
import math
from scipy import stats

from common import consts


sample1 = stats.poisson.rvs(mu=10000, size=20, random_state=1)
sample2 = stats.poisson.rvs(mu=40000, size=20, random_state=1)
sample3 = stats.poisson.rvs(mu=5000, size=20, random_state=1)

__all__ = ['create_workload_generator', 'load_from_file', 'save_as_yaml']

with open('templates/task-template.yaml') as f:
    WORKLOAD_POD_TEMPLATE = f.read()


def create_workload_generator(workload_type: str):
    if workload_type == 'cloud_edge':
        return Cloud2EdgeWorkloadGenerator()
    elif workload_type == 'edge_cloud':
        return Edge2CloudWorkloadGenerator()
    elif workload_type == 'edge_cloud_edge':
        return Edge2Cloud2EdgeWorkloadGenerator()
    raise RuntimeError('Unknown workload type:', workload_type)


def load_from_file(filename: str):
    with open(filename, 'r') as file:
        workload = list(yaml.safe_load_all(file))
        logging.info(f'Workload {filename} loaded, with {len(workload)} jobs')
        return workload


def save_as_yaml(yaml_dict: dict, filename: str):
    with open(filename, 'w') as file:
        yaml.safe_dump_all(yaml_dict, file)


@dataclasses.dataclass
class Task(object):
    start_ms: int = 0
    end_ms: int = 0

    cpu_count: int = 0
    memory_mb: int = 0
    time_ms: int = 0
    server_url: str = 'http://localhost:80'
    send_size_mb: int = 0
    write_size_mb: int = 0

    request_cpu: float = 1
    limit_cpu: float = 1
    request_mem_mb: float = 10
    limit_mem_mb: float = 10

    name: str = None
    job_name: str = None
    task_type: str = None
    node_type: str = None
    scheduler_name: str = None
    container_image: str = consts.TASK_IMAGE


class WorkloadGenerator(object):
    ALIBABA_TRACE_JOBS_JSON = "templates/alibaba-trace-jobs.json"

    def __init__(self, task_types: list):
        self.trace_data = read_json(WorkloadGenerator.ALIBABA_TRACE_JOBS_JSON)
        self.job_count = 0
        self.task_count = 0
        self.task_types = task_types
        self.prev_job_last_start_time = 0

    def _random_choose_job(self):
        return random.choice(self.trace_data)

    def _task_type(self):
        return random.choice(self.task_types)

    def _get_task_parameters(self, task: dict):
        start_ms = task['container.start.ms']
        end_ms = task['container.end.ms']
        cpu = task['cpu']
        max_cpu = task['maxcpu']
        ram = task['ram']
        max_ram = task['maxram']
        io = task['io']
        return self._process_task_parameters(start_ms, end_ms, cpu, max_cpu, ram, max_ram, io)

    @staticmethod
    def _process_task_parameters(start_ms, end_ms, cpu, max_cpu, ram, max_ram, io):
        params = {
            'start_ms': start_ms,
            'end_ms': end_ms,
            'cpu_count': max(1, int(cpu * 16)),
            'memory_mb': int(max_ram * 1024 * 32),
            'time_ms': max(1, int((end_ms - start_ms) * max_cpu * 100)),
            'send_size_mb': int(random.random() * 0.0),
            'write_size_mb': int(io * 1024 * 0.0),
            'request_cpu': cpu * 16,
            'limit_cpu': max_cpu * 16,
            'request_mem_mb': int(ram * 1024 * 32),
            'limit_mem_mb': int(max_ram * 1024 * 32),
        }
        return Task(**params)

    def _job_num(self):
        #return 20
        return 20
        # return random.randint(10, len(self.trace_data))

    def _generate_job(self) -> list:
        pass

    def generate(self):
        jobs = []
        job_num = self._job_num()
        for _ in range(job_num):
            #while self.prev_job_last_start_time<=400000:
            print(self.task_count)
            if self.task_count<=150:
               job = self._generate_job()
               jobs.append(job)
               self.job_count += 1
        return jobs

    def _generate_general_tasks(self, job_dict: dict, first_n: int = 30) -> list:
        task_dict = job_dict['job.tasks']
        tasks = []
        for i, task in enumerate(task_dict):
            if i == first_n:
                break

            task = self._get_task_parameters(task)
            if i == 0:
                task_type = 'cloud'
            elif i == 1:
                task_type = 'edge1'
            elif i == 2 and len(self.task_types) == 3:
                task_type = 'edge2'
            else:
                task_type = self._task_type()
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
            #need_mem_mb = (task.write_size_mb % 128) + (task.write_size_mb / 128) + task.memory_mb + 10
            #task.limit_mem_mb = max(task.limit_mem_mb, need_mem_mb) + 50

            #need_mem_mb = (task.write_size_mb % 128) + (task.write_size_mb / 128) + task.memory_mb + 250
            #200,100
            need_mem_mb = task.write_size_mb + task.memory_mb + 200
            task.limit_mem_mb = max(task.limit_mem_mb, need_mem_mb) + 50

            # Reduces working time
            task.time_ms *= task.limit_cpu
            while task.time_ms >= 300000:
                task.time_ms = int(task.time_ms / 2)
            if task.limit_cpu < 1:
                task.time_ms *= task.limit_cpu

            # Build dictionary
            tasks[i] = build_task_dict(task)

        return tasks


class Cloud2EdgeWorkloadGenerator(WorkloadGenerator):

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:2])

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

        # TODO: temporary edge1
        #for i,t in enumerate(tasks):
        #    if i==0:
        #        t.node_type = 'cloud'

        tasks = self._post_process_tasks(tasks)
        tasks.sort(key=lambda t: t['startTime'])
        min_start_time = min([t['startTime'] for t in tasks])

        for t in tasks:
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + sample1[self.job_count]
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
                    task.request_cpu *= 50
                    task.limit_cpu *= 50
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 16:
                        task.cpu_count = 16
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
                    task.request_cpu *= 12.5
                    task.limit_cpu *= 12.5
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 4:
                        task.cpu_count = 4
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.memory_mb *= 2
                    task.request_mem_mb *= 2
                    task.limit_mem_mb *= 2
                    task.task_type = 'memory'
                edge1_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks


class Edge2CloudWorkloadGenerator(WorkloadGenerator):

    def __init__(self):
        super().__init__(consts.TASK_TYPES[:2])

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
            #t['startTime'] = t['startTime'] - min_start_time + self.prev_job_last_start_time
            t['startTime'] = int((t['startTime'] - min_start_time) * 8 + self.prev_job_last_start_time)

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + sample2[self.job_count]
        print('job start time: ',self.prev_job_last_start_time)
        return tasks

    def _post_process_tasks(self, tasks):
        cloud_task_cnt = 0
        edge1_task_cnt = 0
        for i, task in enumerate(tasks):
            if task.node_type == 'cloud':
                # CPU
                if cloud_task_cnt % 2 == 0:
                    #task.cpu_count *= 4
                    task.request_cpu *= 16
                    task.limit_cpu *= 32
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 16:
                        task.cpu_count = 16
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.memory_mb *= 16
                    task.request_mem_mb *= 16
                    task.limit_mem_mb *= 32
                    task.task_type = 'memory'
                cloud_task_cnt += 1

            elif task.node_type == 'edge1':
                # CPU
                if edge1_task_cnt % 2 == 0:
                    #task.cpu_count *= 25
                    task.request_cpu *= 4
                    task.limit_cpu *= 8
                    task.cpu_count = max(1, math.ceil(task.limit_cpu))
                    if task.cpu_count > 4:
                        task.cpu_count = 4
                    task.task_type = 'cpu'
                # Memory
                else:
                    task.memory_mb *= 8
                    task.request_mem_mb *= 8
                    task.limit_mem_mb *= 16
                    task.task_type = 'memory'
                edge1_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks


class Edge2Cloud2EdgeWorkloadGenerator(WorkloadGenerator):

    def __init__(self):
        super().__init__(consts.TASK_TYPES)

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

        self.prev_job_last_start_time = max([t['startTime'] for t in tasks]) + sample3[self.job_count]
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
                    task.request_mem_mb *= 40
                    task.limit_mem_mb *= 40
                    task.memory_mb = max(int(task.request_mem_mb), int(task.limit_mem_mb))
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
                    task.request_mem_mb *= 10
                    task.limit_mem_mb *= 10
                    task.memory_mb = max(int(task.request_mem_mb), int(task.limit_mem_mb))
                    task.task_type = 'memory'
                edge_task_cnt += 1

        tasks = self._build_dicts(tasks)
        return tasks


def build_task_dict(task: Task):
    if task.node_type not in consts.TASK_TYPES:
        raise RuntimeError('The type %s of workload is supported.' % task.node_type)

    scheduler_name = task.scheduler_name
    if not scheduler_name:
        scheduler_name = consts.DEFAULT_SCHEDULER_NAME

    s = WORKLOAD_POD_TEMPLATE \
        .replace('$NAME', task.name) \
        .replace('$JOB_NAME', task.job_name) \
        .replace('$TASK_TYPE', task.task_type) \
        .replace('$SCHEDULER_NAME', scheduler_name) \
        .replace('$CONTAINER_IMAGE', task.container_image) \
        .replace('$CPU_COUNT', str(task.cpu_count)) \
        .replace('$MEMORY_MB', str(task.memory_mb)) \
        .replace('$ITER_FACTOR', str(int(task.time_ms))) \
        .replace('$SERVER_URL', str(task.server_url)) \
        .replace('$SEND_SIZE_MB', str(round(task.send_size_mb, 2))) \
        .replace('$WRITE_SIZE_MB', str(task.write_size_mb)) \
        .replace('$NODE_TYPE', task.node_type) \
        .replace('$START_TIME', str(task.start_ms)) \
        .replace('$REQUEST_MEM_MB', str(task.request_mem_mb)) \
        .replace('$REQUEST_CPU', str(round(task.request_cpu, 4))) \
        .replace('$LIMIT_MEM_MB', str(task.limit_mem_mb)) \
        .replace('$LIMIT_CPU', str(round(task.limit_cpu, 4)))

    return yaml.load(s, Loader=yaml.SafeLoader)


def read_json(filename):
    with open(filename, "r") as fp:
        data = json.load(fp)
        return data
