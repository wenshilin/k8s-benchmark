import logging

import yaml

from .workload_runner import WorkloadRunner


def load_from_file(filename: str):
    with open(filename, 'r') as file:
        workload = list(yaml.safe_load_all(file))
        logging.info(f'Workload {filename} loaded, with {len(workload)} jobs')
        return workload
