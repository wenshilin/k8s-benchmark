import os

import pandas as pd
import prettytable

import common.utils.kube as utils
from scripts.read_pod_from_file import read_pod_from_file

succeed_headers = ['名称', 'WaitTime_Scheduled(s)', 'WaitTime_Excuted(s)', 'WaitTime(s)', 'ExecutionTime(s)', 'SumTime(s)']
failed_headers = ['名称', 'Job', '提交时间', '创建时间', '开始时间', '结束时间', '负载类型', '选择调度器', '选择节点']
now = ''

pods = read_pod_from_file('../results/2020-12-08-14-01-17-边到云到边-ep.pk')

tts, succeed, failed = [], [], []
succeed_table = prettytable.PrettyTable(succeed_headers)
failed_table = prettytable.PrettyTable(failed_headers)
wait_being_created = []

pods.sort(key=lambda pod: pod.status.start_time)
for p in pods:
    submit_time = utils.get_pod_creation_timestamp(p)
    st = utils.get_pod_start_time(p)
    ft = utils.get_pod_finish_time(p)
    if utils.pod_succeeded(p):
        #ct = utils.get_pod_start_time(p)
        ct = p.status.start_time

        # waittime count
        wt = utils.get_pod_waiting_time(p)
        wt_s = utils.get_pod_beenscheduled_time(p)
        wt_e = utils.get_pod_excutedwaiting_time(p)
        wait_being_created.append(wt_e)

        rt = (ft - st).total_seconds()
        tt = wt + rt
        job = p.metadata.labels.get('job', 'None')
        row = [p.metadata.name, wt_s, wt_e, wt, rt, tt]
        succeed.append(row)
        succeed_table.add_row(row)
        tts.append(tt)
    elif utils.pod_failed(p):
        ct = utils.get_pod_creation_timestamp(p)
        job = p.metadata.labels.get('job', 'None')
        row = [
            p.metadata.name, job, submit_time, ct, st, ft,
            p.metadata.labels.get('taskType'),
            p.metadata.labels.get('linc/schedulerName', utils.get_pod_scheduler_name(p)),
            p.spec.node_name
        ]
        failed.append(row)
        failed_table.add_row(row)
print(succeed_table)
print(failed_table)

df = pd.DataFrame(succeed, columns=succeed_headers)
filename = os.path.join('../results', 'summary-succeed.csv')
df.to_csv(filename)

print(f'等待执行的时间{sum(wait_being_created)}s, 平均时间{sum(wait_being_created) / len(wait_being_created)}s')
