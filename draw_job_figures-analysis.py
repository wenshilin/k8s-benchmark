import os
import pandas as pd

from benchmark.figures import *
from benchmark.job_data_reading import read_data_from_directories


def main():
    # 数据的根目录
    root_dir = 'results/jobs'

    dirs = list_dir(root_dir)
    summary, jobs = read_data_from_directories(dirs)
    algorithm_names = summary['name'].unique()
    print(summary)
    #print(jobs)

    writer = pd.ExcelWriter('C:\\Users\\wenshilin\\Desktop\\jobs-4.xlsx')
    summary.to_excel(writer,index=False)
    writer.save()
    print('Save .xlsx succeed!')

def list_dir(root_dir: str):
    dirs = os.listdir(root_dir)
    return [os.path.join(root_dir, d) for d in dirs]

if __name__ == '__main__':
    main()
