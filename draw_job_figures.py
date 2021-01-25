import logging
import os
import sys

from benchmark.figures.figures import draw_job_figures, list_dir


def draw_one_dir():
    # 数据的根目录
    root_dir = '/Volumes/Data/实验数据/final/ce-624/bra/-0-dt/jobs'
    # root_dir = '/Users/xenon/Desktop/lrp-jobs'
    # root_dir = 'results/jobs'
    # root_dir = "/Users/xenon/Desktop/test/jobs"
    save_dir = '/Volumes/Data/实验数据/final/ce-624/bra/-0-dt'
    # save_dir = 'results'
    draw_job_figures(root_dir, save_dir, treat_model_as_drl=True)


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
            draw_job_figures(job_dir, abs_dir, treat_model_as_drl=True)


def main():
    argv = sys.argv
    if len(argv) == 1:
        draw_one_dir()
    else:
        job_dir = argv[1]
        save_dir = argv[2]
        draw_job_figures(job_dir, save_dir, treat_model_as_drl=True)


if __name__ == '__main__':
    main()
