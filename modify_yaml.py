import json
import os
import yaml
import logging
from benchmark import workload_gen

dirpath = 'E:\\2K20\\k8s-benchmark\\results\\workloads\\2020-11-08 19-30-02'
list1 = ['linc-scheduler-rlp', 'linc-scheduler-bra', 'default-scheduler', 'linc-scheduler-ep',
         'linc-scheduler-lrp', 'linc-scheduler-mrp']
#workload_type = '边到云到边'

for j, info in enumerate(os.listdir(dirpath)):
    domain = os.path.abspath(dirpath)  # 获取文件夹的路径
    filepath = os.path.join(domain, info)  # 将路径与文件名结合起来就是每个文件的完整路径
    print(info)

    with open(os.path.join(dirpath, str(0) + '-' + info), 'w') as file:
        with open(filepath, 'r') as file1:
             jobs = list(yaml.safe_load_all(file1))
             #print(len(jobs))
             joblist = []
             for job in jobs:
                 #print(len(job))
                 podlist = []
                 for pod in job:
                     pod['pod']['metadata']['labels']['jobTaskNumber'] = 'n' + str(len(job))
                     pod['pod']['spec']['schedulerName'] = list1[j]
                     podlist.append(pod)
                 joblist.append(podlist)

             yaml.safe_dump_all(joblist, file)

