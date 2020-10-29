from unittest import TestCase
import unittest
import os
import logging

from benchmark import workload_gen
from common.utils import kube_config


class WorkloadGenTest(TestCase):

    def setUp(self) -> None:
        kube_config.load_kube_config()
        self.out_dir = 'results/workloads/'
        os.makedirs(self.out_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
        )

    def test_trace_data(self):
        data = workload_gen.read_json(workload_gen.WorkloadGenerator.ALIBABA_TRACE_JOBS_JSON)
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
        print('task avg running time ms', avg(running_time_ms), 'max', max(running_time_ms), 'min', min(running_time_ms))
        print('task avg cpu', avg(cpu), 'max', max(cpu), 'min', min(cpu))
        print('task avg max_cpu', avg(max_cpu), 'max', max(max_cpu), 'min', min(max_cpu))
        print('task avg ram', avg(ram), 'max', max(ram), 'min', min(ram))
        print('task avg max_ram', avg(max_ram), 'max', max(max_ram), 'min', min(max_ram))
        print('task avg io', avg(io), 'max', max(io), 'min', min(io))

    def test_generate_workload(self):
        #self.dump('云到边', 'cloud_edge')
        self.dump('边到云', 'edge_cloud')
        # self.dump('边到云到边', 'edge_cloud_edge')

    def dump(self, name: str,  workload_type: str):
        generator = workload_gen.create_workload_generator(workload_type)
        pod_dicts = generator.generate()
        workload_gen.save_as_yaml(pod_dicts, self.out_dir + name + '.yaml')
        self.replace_scheduler(pod_dicts, 'linc-scheduler-configuration-1')
        workload_gen.save_as_yaml(pod_dicts, self.out_dir + name + '-c61.yaml')
        self.replace_scheduler(pod_dicts, 'linc-scheduler-configuration-2')
        workload_gen.save_as_yaml(pod_dicts, self.out_dir + name + '-c71.yaml')
        self.replace_scheduler(pod_dicts, 'linc-scheduler-configuration-3')
        workload_gen.save_as_yaml(pod_dicts, self.out_dir + name + '-c81.yaml')
        self.replace_scheduler(pod_dicts, 'aladdin-scheduler')
        workload_gen.save_as_yaml(pod_dicts, self.out_dir + name + '-c91.yaml')

    def replace_scheduler(self, pods_dicts, scheduler_name):
        for job in pods_dicts:
            for pod in job:
                pod['pod']['spec']['schedulerName'] = scheduler_name


def avg(data: list):
    return sum(data) / len(data)


if __name__ == '__main__':
    unittest.main()
