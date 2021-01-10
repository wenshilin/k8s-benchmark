import logging
import os
import shutil

from benchmark.figures.figures import draw_job_figures
from benchmark.workload_tester.sim_env_workload_tester import SimEnvWorkloadTester
from common.utils import now_str

data_dir = 'results/jobs'
figure_save_dir = 'results/figures'
workload_generated_time = '2021-01-05 18-35-52 bra'


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
    )

    results_dir_exists = os.path.exists('results')
    os.makedirs('results', exist_ok=True)
    if results_dir_exists:
        os.makedirs('old-results', exist_ok=True)
        shutil.move('results', 'old-results')
        os.rename('old-results/results', f'old-results/{now_str()}')
        os.makedirs('results', exist_ok=True)

    SimEnvWorkloadTester(
        # 负载类型
        workload_type='边到云',
        workload_load_directory='workloads',
        # 负载生成时间/负载所在文件夹
        workload_generated_time=workload_generated_time,
        # 需要运行的算法名称
        scheduling_algorithms=['ep', 'lrp', 'mrp', 'bra'],
        # 重复运行的次数，当前为重复运行一种算法repeat_times之后再运行下一算法
        repeat_times=10,
        # 仿真环境服务端端口
        base_url='http://localhost:8001',
    ).run()

    draw_job_figures(data_dir, figure_save_dir)
