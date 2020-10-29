import datetime
import logging
import time
import unittest

import kubernetes

from benchmark import workload_gen
from benchmark.workload_runner import WorkloadRunner
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
        global_arguments.set_argument('evaluation_summary_dir', 'results/summary')
        self.client = kubernetes.client.CoreV1Api()
        self.summarizer = KubeEvaluationSummarizer()

        self.ms = MetricsServerClient('http://localhost:8001/apis/metrics.k8s.io/v1beta1')
        self.workload_runner = WorkloadRunner(self.client, dry_run=False)

    def test_all(self):
        for _ in range(1):
            self.run_once()

    def run_once(self):
        #tests = ['云到边-c10', '云到边-c11', '云到边-c12','云到边-c13']
        # tests = ['云到边-c61', '云到边-c71', '云到边-c81', '云到边-c91']
        #tests = ['云到边-c2', '云到边-c3', '云到边-c4', '云到边-c5']
        #tests = ['云到边-c44', '云到边-c54', '云到边-c64', '云到边-c74']
        # FIXME:
        tests = ['边到云-c61']
        #tests = ['边到云到边-c46', '边到云到边-c56', '边到云到边-c66', '边到云到边-c76']
        #tests = ['云到边-c44']

        for name in tests:
            print("---------------------------------------------------------------------------")
            jobs = workload_gen.load_from_file('results/workloads/%s.yaml' % name)
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
        print('all job finished')

    def start(self, workload):
        self.workload_runner.restart(workload)

    def write_summary(self, name, pods):
        self.now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.summarizer.write_summary(pods, self.now, name)


if __name__ == '__main__':
    unittest.main()
