import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def auto_label(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2. - 0.1, 1.01 * height, str(int(height)))


def draw_makespan(data_frame: pd.DataFrame,
                  algorithm_names,
                  save_filename: str,
                  title: str = None,
                  x_label: str = None,
                  y_label: str = 'Makespan(s)',
                  dir_name: str = 'results/figures'):
    means = []
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        mean = df['makespan'].mean()
        means.append(mean)

    x = algorithm_names
    y = means

    plt.xticks(np.arange(len(x)), x)
    a = plt.bar(np.arange(len(x)), y)
    auto_label(a)

    plt.title(title, fontsize=12)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)

    plt.grid(True)
    plt.show()
