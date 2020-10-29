import yaml

from .cloud_to_edge_workload_generator import Cloud2EdgeWorkloadGenerator
from .edge_to_cloud_to_edge_workload_generator import Edge2Cloud2EdgeWorkloadGenerator
from .edge_to_cloud_workload_generator import Edge2CloudWorkloadGenerator
from .workload_generator import WorkloadGenerator


def create_workload_generator(workload_type: str):
    if workload_type == 'cloud_edge':
        return Cloud2EdgeWorkloadGenerator()
    elif workload_type == 'edge_cloud':
        return Edge2CloudWorkloadGenerator()
    elif workload_type == 'edge_cloud_edge':
        return Edge2Cloud2EdgeWorkloadGenerator()
    raise RuntimeError('Unknown workload type:', workload_type)


def save_as_yaml(yaml_dict: dict, filename: str):
    with open(filename, 'w') as file:
        yaml.safe_dump_all(yaml_dict, file)
