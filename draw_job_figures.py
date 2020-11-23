import os

from benchmark.figures import *
from benchmark.job_data_reading import read_data_from_directories


def main():
    # 数据的根目录
    root_dir = 'results/20-11-21/jobs'

    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)
    algorithm_names = summary['name'].unique()
    print(summary)
    print(jobs)

    os.makedirs('results/figures', exist_ok=True)
    draw_makespan(summary, algorithm_names,
                  title='Edge-Cloud',
                  save_filename='makespan.jpg',
                  x_label='Different scheduling algorithms')
    draw_jct_box(summary, algorithm_names,
                 title='Edge-Cloud',
                 save_filename='jct_box.jpg',
                 x_label='Different scheduling algorithms')
    draw_cdf(jobs, algorithm_names,
             title='Edge-Cloud',
             save_filename='CDF.jpg',
             x_label='Job complete time(s)')


def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs]


if __name__ == '__main__':
    main()
