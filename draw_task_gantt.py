import datetime
import os

import pytz

from benchmark.figures.gantt import draw_pod_gantt
from common.utils import kube as utils
from scripts.read_pod_from_file import read_pod_from_file


def main():
    pickle_filenames = [
        '2021-01-01-09-01-49-云到边-ep.pk',
        '2021-01-01-09-03-45-云到边-lrp.pk',
        '2021-01-01-09-05-21-云到边-mrp.pk',
        '2021-01-01-09-06-56-云到边-bra.pk',
    ]
    pickle_dir = 'results/pods'
    pickle_filenames = [os.path.join(pickle_dir, pf) for pf in pickle_filenames]

    benchmark = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.timezone('UTC'))

    pods = []
    for pf in pickle_filenames:
        pod_list = read_pod_from_file(pf)
        first_start_time = min([utils.get_pod_creation_timestamp(p) for p in pod_list])
        for p in pod_list:
            p.metadata.name = p.metadata.name + '-' + pf.split('-')[-1].split('.')[0]
            p.metadata.creation_timestamp = utils.get_pod_creation_timestamp(p) - first_start_time + benchmark
            p.status.container_statuses[0].state.terminated.started_at = utils.get_pod_start_time(p) - first_start_time + benchmark
            p.status.container_statuses[0].state.terminated.finished_at = utils.get_pod_finish_time(p) - first_start_time + benchmark
        pods.extend(pod_list)

    pods.sort(key=utils.get_obj_name)

    draw_task_gantt(pods)
    draw_task_wait_gantt(pods)
    draw_task_run_gantt(pods)


def draw_task_gantt(pods):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    draw_pod_gantt(
        pods,
        now,
        utils.get_pod_creation_timestamp,
        utils.get_pod_finish_time,
    )


def draw_task_run_gantt(pods):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    draw_pod_gantt(
        pods,
        now,
        utils.get_pod_start_time,
        utils.get_pod_finish_time,
    )


def draw_task_wait_gantt(pods):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    draw_pod_gantt(
        pods,
        now,
        utils.get_pod_creation_timestamp,
        utils.get_pod_start_time,
    )


if __name__ == '__main__':
    main()
