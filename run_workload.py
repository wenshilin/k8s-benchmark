import unittest
import time
import kubernetes
import numpy as np
import datetime
import prettytable
import os
import logging

from common.kube_info.metrics_server_client import MetricsServerClient
from benchmark.workload_runner import WorkloadRunner
from benchmark import workload_gen
from common.utils import kube as utils
from common.utils import kube_config
from common import global_arguments
from common.summarizing.kube_evaluation_summarizer import KubeEvaluationSummarizer


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
        self.summarizer = KubeEvaluationSummarizer(self.client)

        self.ms = MetricsServerClient('http://localhost:8001/apis/metrics.k8s.io/v1beta1')
        self.workload_runner = WorkloadRunner(self.client, dry_run=False)

        #count JCT
        self.JCTheaders = ['Jobname', 'Job Completed Time(s)']

    def test_all(self):
        for _ in range(1):
            self.run_once()

    def run_once(self):
        #tests = ['云到边-c10', '云到边-c11', '云到边-c12','云到边-c13']
        # tests = ['云到边-c61', '云到边-c71', '云到边-c81', '云到边-c91']
        #tests = ['云到边-c2', '云到边-c3', '云到边-c4', '云到边-c5']
        #tests = ['云到边-c44', '云到边-c54', '云到边-c64', '云到边-c74']
        tests = ['边到云-c61', '边到云-c71', '边到云-c81', '边到云-c91']
        #tests = ['边到云到边-c46', '边到云到边-c56', '边到云到边-c66', '边到云到边-c76']
        #tests = ['云到边-c44']

        for name in tests:
            print("---------------------------------------------------------------------------")
            jobs = workload_gen.load_from_file('results/workloads/%s.yaml' % name)
            print('Running %s' % name)
            print('loaded job number: %d' % len(jobs))
            #for i in range(len(jobs)):
            self.start(name, jobs)
            self.summarizer.write_summary(name)

            print("---------------------------------------------------------------------------")
            self.now = datetime.datetime.now()

            JCT_table = prettytable.PrettyTable(self.JCTheaders)
            JCT_dir = os.path.join('results/count_JCT/', '%s-%s' % (str(self.now), name))
            os.makedirs(JCT_dir, exist_ok=True)
            savefilename = os.path.join(JCT_dir, 'coutJCT.md')
            savefile = os.path.join(JCT_dir, 'coutJCT.csv')

            pods = self.client.list_namespaced_pod('default').items
            joblist = []
            for i, p in enumerate(pods):
                job = p.metadata.labels.get('job', 'None')
                for j in range(20):
                    if job == 'job-' + str(j):
                        joblist.append(job)
            joblist1 = list(np.unique(joblist))

            with open(savefilename, 'w') as f:
                f.write('Jobname,'+'Job Completed Time(s)'+'\n')
                countJCT = []
                for job1 in joblist1:
                    tasks = []
                    jobstarttime, jobendtime = [], []
                    for p in pods:
                        job = p.metadata.labels.get('job', 'None')
                        if job == job1:
                            tasks.append(p.metadata.name)
                            jobstarttime.append(p.status.start_time)
                            jobendtime.append(p.status.container_statuses[0].state.terminated.finished_at)

                    # Job Completed Times
                    JCTs = (max(jobendtime) - min(jobstarttime)).total_seconds()

                    #print('Job Completed Time(s) of ' + job1 + ' is: ', JCTs)
                    f.write(job1+','+str(JCTs)+"\n")
                    JCT_row = [job1, JCTs]
                    JCT_table.add_row(JCT_row)
                    countJCT.append(JCTs)

                print(JCT_table)
                JCTsummary = 'Job平均时长：%.2fs，最小时长：%.2fs，最大时长：%.2fs。' % (sum(countJCT) / len(countJCT), min(countJCT), max(countJCT))
                logging.info(JCTsummary)
                f.write(JCTsummary)
            f.close()

            f1 = open(savefile, 'a')
            f1.write(str(JCT_table))
            f1.close()

    def start(self, name, workload):
        self.workload_runner.restart(workload)

        all_pod_finished = False
        t = 0
        while not all_pod_finished or not self.workload_runner.has_done():
            t += 1
            time.sleep(5)
            pods = self.client.list_namespaced_pod('default').items
            all_pod_finished = all(map(utils.pod_finished, pods))

        print('finished')


if __name__ == '__main__':
    unittest.main()
