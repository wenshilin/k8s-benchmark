import datetime
import os
from typing import *

import plotly as py
import plotly.figure_factory as ff
from kubernetes.client import V1Pod

from common.utils import kube as utils

pyplt = py.offline.plot


def draw_pod_gantt(pods: List[V1Pod], filename: str, start_func, finish_func):
    pod_dicts = []
    colors = {}
    jobs = set()
    for pod in pods:
        job_name = utils.get_pod_job_name(pod)
        pod_dicts.append({
            'Task': utils.get_obj_name(pod),
            'Start': start_func(pod) + datetime.timedelta(hours=8),
            'Finish': finish_func(pod) + datetime.timedelta(hours=8),
            'Type': job_name
        })
        jobs.add(job_name)

    default_colors = py.colors.DEFAULT_PLOTLY_COLORS
    for idx, job_name in enumerate(jobs):
        colors[job_name] = default_colors[idx % len(default_colors)]

    draw_gantt(pod_dicts, colors, filename)


def create_gantt_data(pods: List[V1Pod], data_type: str):
    pod_dicts = []
    jobs = {}
    for pod in pods:
        job_name = utils.get_pod_job_name(pod)
        if job_name not in jobs:
            jobs[job_name] = []
        else:
            jobs[job_name].append(pod)

    for job_name, pods in jobs.items():
        first_creation_timestamp = min([utils.get_pod_creation_timestamp(pod) for pod in pods])
        last_finish_time = max([utils.get_pod_finish_time(pod) for pod in pods])
        pod_dicts.append({
            'Task': f"{job_name}-{data_type}",
            'Start': first_creation_timestamp,
            'Finish': last_finish_time,
            'Type': data_type
        })
    return pod_dicts


def draw_gantt(data: list, colors: dict, filename: str):
    fig = ff.create_gantt(data, colors=colors, index_col='Type', group_tasks=True)
    os.makedirs('results/gantt', exist_ok=True)
    pyplt(fig, filename=f'results/gantt/{filename}.html', image_height=1800)
