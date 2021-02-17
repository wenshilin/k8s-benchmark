import logging

import pandas as pd

from benchmark.figures.figures import *

scenarios = ['ce', 'ec', 'ece']
times = ['06', '624']
resources = ['-0', '-25', '-50', '+25', '+50']

base_dir = '/Volumes/Data/实验数据/final'
algorithm_ns = algorithms.copy()
algorithm_ns.insert(0, drl_name)


def get_data(
        root_dir: str,
        treat_model_as_drl: bool = False,
):
    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)

    if treat_model_as_drl:
        rename_model_as_drl(summary, jobs)

    algorithm_names = summary['name'].unique()
    if drl_name in algorithm_names:
        algorithm_names = list(algorithm_names)
        algorithm_names.remove(drl_name)
        algorithm_names.insert(0, drl_name)
    print(summary)
    print(jobs)

    return summary, jobs


final_data = None
for r in resources:
    for s in scenarios:
        for t in times:
            try:
                wd = os.path.join(base_dir, f'{s}-{t}', 'mix', r, 'jobs')
                summary, jobs = get_data(wd, True)
                print(summary)
                workload_type_cn = '云到边'
                if s == 'ec':
                    workload_type_cn = '边到云'
                elif s == 'ece':
                    workload_type_cn = '云到边到云'

                workload_time_cn = '0-6h'
                if t == '624':
                    workload_time_cn = '6-24h'

                resource_cn = r
                if r == '-0':
                    resource_cn = '资源不变'
                means = {
                    '场景': workload_type_cn,
                    '时间': workload_time_cn,
                    '资源变化': resource_cn,
                }
                for an in algorithm_ns:
                    df = summary[summary['name'] == an]
                    mean = df['mean(jct)'].mean()
                    means[an] = round(mean, 2)
                df = pd.Series(means).to_frame().T
                if final_data is None:
                    final_data = df
                else:
                    final_data = pd.concat([final_data, df])

            except Exception as e:
                logging.exception(e)

print(final_data)

with pd.ExcelWriter('jct avg.xlsx') as ew:
    final_data.to_excel(ew)
