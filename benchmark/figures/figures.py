import datetime
import os

from matplotlib import pyplot as plt

from .jct_avg import draw_jct_avg
from .jct_box import draw_jct_box
from .makespan import draw_makespan
from ..job_data_reading import read_data_from_directories


def convert_name(name):
    return 'drl' if name.isdigit() else name


def rename_model_as_drl(summary, jobs):
    jobs['name'] = jobs['name'].map(convert_name)
    summary['name'] = summary['name'].map(convert_name)


# 绘制makespan柱状图，JCT盒图，以及JCT的CDF
def draw_job_figures(
        root_dir: str,
        save_dir: str,
        treat_model_as_drl: bool = False,
        save_filename: str = None,
        show_figure: bool = True,
):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    save_filename = save_filename or root_dir.replace('/', '_') + now + ".png"

    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)

    if treat_model_as_drl:
        rename_model_as_drl(summary, jobs)

    algorithm_names = summary['name'].unique()
    if 'drl' in algorithm_names:
        algorithm_names = list(algorithm_names)
        algorithm_names.remove('drl')
        algorithm_names.insert(0, 'drl')
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
    draw_jct_avg(summary, algorithm_names,
                 title='JCT on average',
                 x_label='Different scheduling algorithms')
    # draw_cdf(jobs, algorithm_names,
    #          title='JCT CDF',
    #          x_label='Job complete time(s)')
    plt.savefig(os.path.join(save_dir, save_filename))
    if show_figure:
        plt.show()


def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs if os.path.isdir(os.path.join(root_dir, d))]
