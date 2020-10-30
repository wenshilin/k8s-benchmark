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
        self.JCTheaders = ['Jobname', 'Job Start Time', 'Job End Time', 'Job Completed Time(s)']
        self.now = ''

    def write_summary(self, pods, now: str, name: str):
        self.now = now
        print("----------------------------------------------------------------------")
        JCT_table = prettytable.PrettyTable(self.JCTheaders)
        JCT_dir = os.path.join(self.save_dir, '%s-%s' % (str(self.now), name))
        os.makedirs(JCT_dir, exist_ok=True)
        savefilename = os.path.join(JCT_dir, 'coutJCT.csv')
        savefile = os.path.join(JCT_dir, 'coutJCT.md')

        joblist = []
        allpodlist = []
        alljobstarttime = []
        alljobendtime = []
        for i, p in enumerate(pods):

            # all pod list
            allpodlist.append(p.metadata.name)
            alljobstarttime.append(p.metadata.creation_timestamp)
            alljobendtime.append(p.status.container_statuses[0].state.terminated.finished_at)
            job_makespan = (max(alljobendtime) - min(alljobstarttime)).total_seconds()

            # all job list
            job = p.metadata.labels.get('job', 'None')
            for j in range(20):
                if job == 'job-' + str(j):
                    joblist.append(job)
        joblist1 = list(np.unique(joblist))

        with open(savefilename, 'w') as f:
            f.write('Jobname,'+'Job Start Time,'+'Job End Time,'+'Job Completed Time(s)'+'\n')
            countJCT = []
            for job1 in joblist1:
                tasks = []
                jobstarttime, jobendtime = [], []
                for p in pods:
                    job = p.metadata.labels.get('job', 'None')
                    if job == job1:
                        tasks.append(p.metadata.name)
                        jobstarttime.append(p.metadata.creation_timestamp)
                        jobendtime.append(p.status.container_statuses[0].state.terminated.finished_at)

                # Job Completed Times
                JCTs = (max(jobendtime) - min(jobstarttime)).total_seconds()
                Job_starttime = min(jobstarttime)
                Job_endtime = max(jobendtime)

                f.write(job1+','+str(Job_starttime)+','+str(Job_endtime)+','+str(JCTs)+"\n")
                JCT_row = [job1, Job_starttime, Job_endtime, JCTs]
                JCT_table.add_row(JCT_row)
                countJCT.append(JCTs)

            print(JCT_table)
            JCTsummary = '总计运行了%d个Job。\n' % (len(countJCT))
            JCTsummary += 'Job平均时长：%.2fs，最小时长：%.2fs，最大时长：%.2fs。' % (sum(countJCT) / len(countJCT), min(countJCT), max(countJCT))
            logging.info(JCTsummary)
            logging.info('Jobs的MakeSpan is：%.2fs。' % (job_makespan))
        f.close()

        f1 = open(savefile, 'a')
        f1.write('# ' + name)
        f1.write('\n')
        f1.write(str(JCT_table))
        f1.write('\n')
        f1.write('Summary: ')
        f1.write('\n')
        f1.write(JCTsummary)
        f1.write('\n')
        f1.write('Jobs的MakeSpan is：%.2fs。\n' % (job_makespan))
        f1.close()
