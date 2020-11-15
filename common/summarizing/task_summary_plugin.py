import logging
import os

import pandas as pd
import prettytable

from .summary_plugin import SummaryPlugin
from ..utils import kube as utils


class TaskSummaryPlugin(SummaryPlugin):
    """
    Task级别的总结，包含Task的内容表，以及Task complete time等信息
    """
    def __init__(self):
        self.save_dir = 'results/tasks'

        self.succeed_headers = ['名称', 'Job', '提交时间', '创建时间', '开始时间', '结束时间', 'WaitTime(s)', 'ExecutionTime(s)', 'SumTime(s)', '负载类型', '选择调度器', '选择节点']
        self.failed_headers = ['名称', 'Job', '提交时间', '创建时间', '开始时间', '结束时间', '负载类型', '选择调度器', '选择节点']
        self.now = ''

    def write_summary(self, pods, now: str, summary_name: str):
        self.now = now
        tts, succeed, failed = [], [], []
        succeed_table = prettytable.PrettyTable(self.succeed_headers)
        failed_table = prettytable.PrettyTable(self.failed_headers)

        pods.sort(key=lambda pod: utils.get_obj_name(pod))
        for p in pods:
            if utils.pod_succeeded(p):
                submitTime = p.metadata.creation_timestamp
                ct = p.status.start_time
                st = p.status.container_statuses[0].state.terminated.started_at
                ft = p.status.container_statuses[0].state.terminated.finished_at
                wt = utils.get_pod_waiting_time(p)
                rt = (ft - st).total_seconds()
                tt = wt + rt
                job = p.metadata.labels.get('job', 'None')
                row = [p.metadata.name, job, submitTime, ct, st, ft, wt, rt, tt,
                       p.metadata.labels.get('taskType'),
                       p.metadata.labels.get('linc/schedulerName', utils.get_pod_scheduler_name(p)),
                       p.spec.node_name]
                succeed.append(row)
                succeed_table.add_row(row)
                tts.append(tt)
            elif utils.pod_failed(p):
                ct = p.metadata.creation_timestamp
                job = p.metadata.labels.get('job', 'None')
                row = [
                    p.metadata.name, job, submitTime, ct, st, ft,
                    p.metadata.labels.get('taskType'),
                    p.metadata.labels.get('linc/schedulerName', utils.get_pod_scheduler_name(p)),
                    p.spec.node_name
                ]
                failed.append(row)
                failed_table.add_row(row)
        print(succeed_table)
        print(failed_table)

        save_dir = os.path.join(self.save_dir, '%s-%s' % (str(self.now), summary_name))
        os.makedirs(save_dir, exist_ok=True)
        if len(tts):
            summary = 'Task平均时长：%.2fs，最小时长：%.2fs，最大时长：%.2fs。' % (sum(tts) / len(tts), min(tts), max(tts))
            logging.info(summary)
            df = pd.DataFrame(succeed, columns=self.succeed_headers)
            filename = os.path.join(save_dir, 'summary-succeed.csv')
            df.to_csv(filename)
            df = pd.DataFrame(failed, columns=self.failed_headers)
            filename = os.path.join(save_dir, 'summary-failed.csv')
            df.to_csv(filename)
            s = self._print_summary(succeed, failed)
            self._save(summary_name, save_dir, succeed_table, failed_table, summary, s)
        else:
            logging.info('获取总结失败（负载列表为空）')

    def _save(self, name, save_dir, *args):
        save_filename = os.path.join(save_dir, 'summary.md')
        with open(save_filename, 'w') as f:
            f.write(SUMMARY_TEMPLATE.format(name, *args))
        logging.info('实验数据已保存 (%s)' % save_filename)

    def _print_summary(self, succeed, failed):
        cloud, edge1, edge2 = [], [], []
        nodes = [['k8s2-54', 'k8s3-54'], ['k8s4-54', 'k8s5-54'], ['k8s6-54', 'k8s7-54']]

        k8s2, k8s3, k8s4, k8s5, k8s6, k8s7 = [], [], [], [], [], []
        nodeslist = ['k8s2-54', 'k8s3-54', 'k8s4-54', 'k8s5-54', 'k8s6-54', 'k8s7-54']

        for row in succeed:
            time = float(row[8])
            task_type = row[9]
            node = row[11]

            if node == nodeslist[0]:
                k8s2.append(time)
            elif node ==nodeslist[1]:
                k8s3.append(time)
            elif node == nodeslist[2]:
                k8s4.append(time)
            elif node == nodeslist[3]:
                k8s5.append(time)
            elif node == nodeslist[4]:
                k8s6.append(time)
            elif node == nodeslist[5]:
                k8s7.append(time)

            if node in nodes[0]:
                cloud.append(time)
            elif node in nodes[1]:
                edge1.append(time)
            elif node in nodes[2]:
                edge2.append(time)
            else:
                raise RuntimeError('node %s not in node set' % (node, ))

        s = '总计启动了%d个Task，%d个运行于云端，其中%d个运行于边缘端1，其中%d个运行于边缘端2。\n' % (len(cloud + edge1 + edge2), len(cloud), len(edge1), len(edge2))
        s += '其中，%d个运行于k8s2，%d个运行于k8s3, %d个运行于k8s4, %d个运行于k8s5, %d个运行于k8s6, %d个运行于k8s7。\n' % (len(k8s2), len(k8s3), len(k8s4), len(k8s5), len(k8s6),len(k8s7))
        if len(cloud):
            s += '云端Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(cloud) / len(cloud), min(cloud), max(cloud))

        if len(edge1):
            s += '边缘端1Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(edge1) / len(edge1), min(edge1), max(edge1))

        if len(edge2):
            s += '边缘端2Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(edge2) / len(edge2), min(edge2), max(edge2))

        if len(k8s2):
            s += 'k8s2节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s2) / len(k8s2), min(k8s2), max(k8s2))

        if len(k8s3):
            s += 'k8s3节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s3) / len(k8s3), min(k8s3), max(k8s3))

        if len(k8s4):
            s += 'k8s4节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s4) / len(k8s4), min(k8s4), max(k8s4))

        if len(k8s5):
            s += 'k8s5节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s5) / len(k8s5), min(k8s5), max(k8s5))

        if len(k8s6):
            s += 'k8s6节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s6) / len(k8s6), min(k8s6), max(k8s6))

        if len(k8s7):
            s += 'k8s7节点Task平均时长：%.1fs，最小时长：%.1fs，最大时长：%.1fs。\n' % (sum(k8s7) / len(k8s7), min(k8s7), max(k8s7))

        if len(failed):
            s += f'共{len(failed)}个负载运行失败。\n'

        return s


SUMMARY_TEMPLATE = """ \
# {0}

Succeed Pods:
```
{1}
```

Failed Pods:
```
{2}
```

Summary:
{3}
{4}
"""
