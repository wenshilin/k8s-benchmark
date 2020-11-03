import yaml
import logging

from .cloud_to_edge_workload_generator import Cloud2EdgeWorkloadGenerator
from .edge_to_cloud_to_edge_workload_generator import Edge2Cloud2EdgeWorkloadGenerator
from .edge_to_cloud_workload_generator import Edge2CloudWorkloadGenerator
from .high_cpu_memory_workload_generator import HighCpuAndMemoryWorkloadGenerator
from .workload_generator import WorkloadGenerator


def create_workload_generator(workload_type: str):
    if workload_type == 'cloud_edge':
        return Cloud2EdgeWorkloadGenerator()
    elif workload_type == 'edge_cloud':
        return Edge2CloudWorkloadGenerator()
    elif workload_type == 'edge_cloud_edge':
        return Edge2Cloud2EdgeWorkloadGenerator()
    elif workload_type == 'high_cpu_memory':
        return  HighCpuAndMemoryWorkloadGenerator()
    raise RuntimeError('Unknown workload type:', workload_type)


def save_as_yaml(yaml_dict: dict, filename: str):
    with open(filename, 'w') as file:
        yaml.safe_dump_all(yaml_dict, file)


def load_from_file(filename: str):
    with open(filename, 'r') as file:
        workload = list(yaml.safe_load_all(file))
        logging.info(f'Workload {filename} loaded, with {len(workload)} jobs')
        return workload

