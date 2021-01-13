import logging
import warnings

from benchmark.figures.figures import draw_job_figures
from benchmark.workload_tester import SimEnvWorkloadTester
from common import global_arguments

if __name__ == '__main__':
    """
    该函数用于运行仿真环境下的负载
    """
    warnings.simplefilter('ignore', ResourceWarning)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
    )
    global_arguments.init_empty_arguments()

    workload_tester = SimEnvWorkloadTester(
        # 负载类型
        workload_type='边到云',
        workload_load_directory='workloads-10',
        # 负载生成时间/负载所在文件夹
        workload_generated_time='2021-01-13 17-43-01',
        # 需要运行的算法名称
        scheduling_algorithms=['ep', 'lrp', 'mrp', 'bra'],
        # 重复运行的次数，当前为重复运行一种算法repeat_times之后再运行下一算法
        repeat_times=10,
        # 仿真环境服务端端口
        base_url='http://localhost:8002',
        # 节点配置文件
        node_conf='common/nodes/c2e2.yaml',
    )
    workload_tester.run()

    draw_job_figures('results/jobs', 'results/figures')
