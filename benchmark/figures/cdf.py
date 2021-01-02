import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def draw_cdf(data_frame: pd.DataFrame,
             algorithm_names,
             title: str = None,
             x_label: str = None,
             y_label: str = 'CDF'):
    max_jct = data_frame['Job Completed Time(s)'].max()
    max_jct_int = math.ceil(max_jct) + 1

    for an in algorithm_names:
        df = data_frame[data_frame['name'] == an]
        job_cnt = df.shape[0]
        jct_list = df['Job Completed Time(s)'].sort_values()
        cdf_list = [0] * max_jct_int
        last_idx = 0
        for idx, jct in enumerate(jct_list):
            jct_int = int(jct)
            cnt = idx + 1
            cdf_list[jct_int] = cnt / job_cnt

            # 填充上一个数据到当前数据的数目，保证图像连续性
            for i in range(last_idx + 1, jct_int):
                cdf_list[i] = cnt / job_cnt
            last_idx = jct_int

        # 填充已完成算法的数据
        for i in range(last_idx + 1, max_jct_int):
            cdf_list[i] = 1

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

        plt.plot(np.arange(max_jct_int), cdf_list, '-', linewidth=2)
        plt.legend(labels=algorithm_names, loc='best')
