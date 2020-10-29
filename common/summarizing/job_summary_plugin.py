import logging
import os

import numpy as np
import prettytable

from .summary_plugin import SummaryPlugin


class JobSummaryPlugin(SummaryPlugin):
    """
    Job 相关的总结，包括JCT
    """
    def __init__(self):
        self.save_dir = 'results/jobs'
        self.JCTheaders = ['Jobname', 'Job Completed Time(s)']
        self.now = ''

    def write_summary(self, pods, now: str, name: str):
        self.now = now
        print("---------------------------------------------------------------------------")
        JCT_table = prettytable.PrettyTable(self.JCTheaders)
        JCT_dir = os.path.join(self.save_dir, '%s-%s' % (str(self.now), name))
        os.makedirs(JCT_dir, exist_ok=True)
        savefilename = os.path.join(JCT_dir, 'coutJCT.md')
        savefile = os.path.join(JCT_dir, 'coutJCT.txt')

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
