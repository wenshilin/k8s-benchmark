import abc
import logging
from typing import List


class AbstractWorkloadTester(object):

    def __init__(self,
                 workload_type: str,
                 workload_generated_time: str,
                 scheduling_algorithms: List[str],
                 repeat_times: int,
                 workload_directory: str):
        self.workload_type = workload_type
        self.workload_generated_time = workload_generated_time
        self.scheduling_algorithms = scheduling_algorithms
        self.repeat_times = repeat_times
        self.workload_load_directory = workload_directory

    def run(self):
        tests = self.generate_tests()
        logging.info(f'workload is generated at {self.workload_generated_time}')
        logging.info(f'attempts to run tests in order: {tests}')
        self.run_tests(tests)

    @abc.abstractmethod
    def run_tests(self, tests):
        pass

    def generate_tests(self):
        tests = []
        for scheduling_algorithm in self.scheduling_algorithms:
            single_algorithm = ['%s-%s' % (self.workload_type, scheduling_algorithm,) for _ in range(self.repeat_times)]
            tests.extend(single_algorithm)
        return tests
