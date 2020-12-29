import datetime
import os

from benchmark.figures.gantt import draw_pod_gantt
from common.utils import kube as utils
from scripts.read_pod_from_file import read_pod_from_file


def main():
    pickle_filenames = [
        '2020-12-23-10-21-54-drl.pk',
        '2020-12-21-11-25-17-云到边-lrp.pk'
    ]
    pickle_dir = 'results/pods'
    pickle_filenames = [os.path.join(pickle_dir, pf) for pf in pickle_filenames]

    pods = []
    for pf in pickle_filenames:
        pod_list = read_pod_from_file(pf)
        for p in pod_list:
            p.metadata.name = p.metadata.name + '-' + pf.split('-')[-1].split('.')[0]
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
