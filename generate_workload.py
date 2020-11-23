import datetime
import logging
import os
import random
import unittest
from unittest import TestCase

from benchmark import workload_gen
from common.utils.json import read_json_file


class WorkloadGenTest(TestCase):

    def setUp(self) -> None:
        self.out_dir = 'results/workloads/'
        os.makedirs(self.out_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
        )
        self.now = ''

        # 随机种子设置，确定每次task个数
        random.seed(1)

    def test_trace_data(self):
        data = read_json_file(workload_gen.WorkloadGenerator.ALIBABA_TRACE_JOBS_JSON)
        print('job cnt:', len(data))
        print('job tasks:', [len(job['job.tasks']) for job in data])

        running_time_ms = []
        start_time_ms = []
        cpu, max_cpu, ram, max_ram, io = [], [], [], [], []
        for job in data:
            for task in job['job.tasks']:
                running_time_ms.append(int(task['container.end.ms'] - int(task['container.start.ms'])))
                start_time_ms.append(int(task['container.start.ms']))
                cpu.append(task['cpu'])
                max_cpu.append(task['maxcpu'])
                ram.append(task['ram'])
                max_ram.append(task['maxram'])
                io.append(task['io'])
        print('task avg running time s', avg(running_time_ms), 'max', max(running_time_ms), 'min', min(running_time_ms))
        print('task avg cpu', avg(cpu), 'max', max(cpu), 'min', min(cpu))
        print('task avg max_cpu', avg(max_cpu), 'max', max(max_cpu), 'min', min(max_cpu))
        print('task avg ram', avg(ram), 'max', max(ram), 'min', min(ram))
        print('task avg max_ram', avg(max_ram), 'max', max(max_ram), 'min', min(max_ram))
        print('task avg io', avg(io), 'max', max(io), 'min', min(io))

    def test_generate_workload(self):
        self.now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        #self.dump('云到边', 'cloud_edge')
        #self.dump('边到云', 'edge_cloud')
        self.dump('边到云到边', 'edge_cloud_edge')
       # self.dump('高Cpu和Memory', 'high_cpu_memory')

    def dump(self, name: str,  workload_type: str):
        generator = workload_gen.create_workload_generator(workload_type)
        pod_dicts = generator.generate()
        out_dir = os.path.join(self.out_dir, self.now)
        os.makedirs(out_dir, exist_ok=True)
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-as_basic.yaml' % (name,)))

        self.replace_scheduler(pod_dicts, 'linc-scheduler-bra')
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-bra.yaml' % (name,)))

        self.replace_scheduler(pod_dicts, 'linc-scheduler-ep')
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-ep.yaml' % (name,)))

        self.replace_scheduler(pod_dicts, 'linc-scheduler-lrp')
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-lrp.yaml' % (name,)))

        self.replace_scheduler(pod_dicts, 'linc-scheduler-mrp')
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-mrp.yaml' % (name,)))

        self.replace_scheduler(pod_dicts, 'linc-scheduler-rlp')
        workload_gen.save_as_yaml(pod_dicts, os.path.join(out_dir, '%s-rlp.yaml' % (name,)))

    def replace_scheduler(self, pods_dicts, scheduler_name):
        for job in pods_dicts:
            for pod in job:
                pod['pod']['spec']['schedulerName'] = scheduler_name


def avg(data: list):
    return sum(data) / len(data)


if __name__ == '__main__':
    unittest.main()
