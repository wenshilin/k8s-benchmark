import datetime
import logging
import os
import time
import unittest
import warnings

import kubernetes

from benchmark import workload_gen
from common.workload.workload_runner import WorkloadRunner
from common import global_arguments
from common.kube_info.metrics_server_client import MetricsServerClient
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer
from common.utils import kube as utils
from common.utils import kube_config


class WorkloadTest(unittest.TestCase):

    def setUp(self) -> None:
        kube_config.load_kube_config()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
        )
        global_arguments.init_empty_arguments()
        self.client = kubernetes.client.CoreV1Api()
        self.summarizer = KubeEvaluationSummarizer()

        self.ms = MetricsServerClient('http://localhost:8001/apis/metrics.k8s.io/v1beta1')
        self.workload_runner = WorkloadRunner(self.client, dry_run=False)

        warnings.simplefilter('ignore', ResourceWarning)

    def test_all(self):
        for _ in range(1):
            self.run_once()

    def run_once(self):
        # 负载的类型
        workload_type = '边到云到边'
        # 负载生成时间/负载所在文件夹
        workload_generated_time = '2020-11-02 16-42-57'

        scheduling_algorithms = ['ep', 'lrp', 'mrp', 'aladdin', 'bra']
        # scheduling_algorithms = ['mrp']
        tests = ['%s-%s' % (workload_type, scheduling_algorithm, ) for scheduling_algorithm in scheduling_algorithms]

        workload_dir = os.path.join('results/workloads', workload_generated_time)

        for name in tests:
            print("-----------------------------------------------------------------")
            jobs = workload_gen.load_from_file(os.path.join(workload_dir, '%s.yaml' % (name, )))
            print('Running %s' % name)
            print('loaded job number: %d' % len(jobs))
            self.start(jobs)
            self.wait_until_all_job_done()
            pods = self.get_pods()
            self.write_summary(name, pods)

    def get_pods(self):
        return self.client.list_namespaced_pod('default').items

    def wait_until_all_job_done(self):
        all_pod_finished = False
        t = 0
        while not all_pod_finished or not self.workload_runner.has_done():
            t += 1
            time.sleep(5)
            pods = self.get_pods()
            all_pod_finished = all(map(utils.pod_finished, pods))
        print('all job finished!!!')
        print("----------------------------------------------------------------------")

    def start(self, workload):
        self.workload_runner.restart(workload)

    def write_summary(self, name, pods):
        self.now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        self.summarizer.write_summary(pods, self.now, name)


if __name__ == '__main__':
    unittest.main()
