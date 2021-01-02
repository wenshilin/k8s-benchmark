import os

from benchmark.figures import *
from benchmark.job_data_reading import read_data_from_directories


def main():
    # 数据的根目录
    root_dir = 'results/jobs'
    #root_dir = '/Volumes/Data/实验数据/ece-morning-sim52_53-c4e2/used-jobs'
    # root_dir = '/Users/xenon/Desktop/casco/results/jobs'

    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)
    algorithm_names = summary['name'].unique()
    print(summary)
    print(jobs)

    os.makedirs('results/figures', exist_ok=True)
    draw_makespan(summary, algorithm_names,
                  title='Cloud-Edge',
                  save_filename='makespan.jpg',
                  x_label='Different scheduling algorithms')
    draw_jct_box(jobs, algorithm_names,
                 title='Cloud-Edge',
                 save_filename='jct_box.jpg',
                 x_label='Different scheduling algorithms')
    draw_cdf(jobs, algorithm_names,
             title='Cloud-Edge',
             save_filename='CDF.jpg',
             x_label='Job complete time(s)')


def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs if os.path.isdir(os.path.join(root_dir, d))]


if __name__ == '__main__':
    main()
