import logging
import os

from benchmark.figures.figures import draw_job_figures, list_dir


def draw_one_dir():
    # 数据的根目录
    #root_dir = '/Volumes/Data/实验数据/transfer/lrp1-54-directly_transfered-undone/used-jobs'
    # root_dir = '/Users/xenon/Desktop/casco/results/jobs'
    root_dir = 'results/jobs'
    # root_dir = "/Users/xenon/Desktop/lrp/used-jobs"
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
