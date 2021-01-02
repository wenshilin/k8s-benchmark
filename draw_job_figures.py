import datetime
import logging
import os

from matplotlib import pyplot as plt

from benchmark.figures import *
from benchmark.job_data_reading import read_data_from_directories


# 绘制makespan柱状图，JCT盒图，以及JCT的CDF
def draw_job_figures(
        root_dir: str,
        save_dir: str,
        save_filename: str = None,
):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    save_filename = save_filename or root_dir.replace('/', '_') + now + ".png"

    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)
    algorithm_names = summary['name'].unique()
    print(summary)
    print(jobs)

    os.makedirs(save_dir, exist_ok=True)

    plt.figure(figsize=(18, 6))
    plt.subplot(131)
    draw_makespan(summary, algorithm_names,
                  title='Makespan',
                  x_label='Different scheduling algorithms')

    plt.subplot(132)
    draw_jct_box(jobs, algorithm_names,
                 title='JCT box',
                 x_label='Different scheduling algorithms')

    plt.subplot(133)
    draw_cdf(jobs, algorithm_names,
             title='JCT CDF',
             x_label='Job complete time(s)')
    plt.savefig(os.path.join(save_dir, save_filename))
    plt.show()


def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs if os.path.isdir(os.path.join(root_dir, d))]


def draw_one_dir():
    # 数据的根目录
    root_dir = '/Volumes/Data/实验数据/_running-ece-morning-t2_sim52_55-c4e2/used-jobs/'
    # root_dir = '/Users/xenon/Desktop/casco/results/jobs'
    root_dir = 'results/jobs'
    save_dir = 'results/figures'
    draw_job_figures(root_dir, save_dir)


def draw_multi_dirs():
    # 数据的根目录
    root_dir = '/Volumes/Data/实验数据'
    dirs = list_dir(root_dir)
    save_dir = 'results/figures'

    for d in dirs:
        abs_dir = os.path.join(root_dir, d)
        is_exp_dir = any(map(lambda path: path == '结果.png', os.listdir(abs_dir)))
        if is_exp_dir:
            job_dir = os.path.join(abs_dir, 'used-jobs')
            logging.info(f'planting {job_dir}...')
            draw_job_figures(job_dir, abs_dir)


if __name__ == '__main__':
    draw_one_dir()
