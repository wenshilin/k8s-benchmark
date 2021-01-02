import matplotlib.pyplot as plt
import pandas as pd


def draw_jct_box(data_frame: pd.DataFrame,
                 algorithm_names,
                 title: str = None,
                 x_label: str = None,
                 y_label: str = 'JCT(s)'):
    data = []
    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        data.append(df['Job Completed Time(s)'])

    plt.boxplot(data, notch=False, sym='o', vert=True, patch_artist=False, showmeans=True,
                showfliers=False,
                meanprops={'marker': 'o', 'markerfacecolor': 'magenta', 'markersize': 3},
                medianprops={'color': 'red', 'linewidth': 3})

    plt.xticks([x + 1 for x in range(len(data))], algorithm_names)

    plt.title(title, fontsize=12)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)

    plt.grid(True)
