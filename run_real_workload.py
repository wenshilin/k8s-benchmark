import logging
import time
import warnings

from benchmark.figures.figures import draw_job_figures
from benchmark.workload_tester import RealEnvWorkloadTester
from common import global_arguments
from common.utils import kube_config

if __name__ == '__main__':
    """
    该函数用于运行真实环境下的负载
    """
    warnings.simplefilter('ignore', ResourceWarning)
    kube_config.load_kube_config()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
    )
    global_arguments.init_empty_arguments()

    workload_tester = RealEnvWorkloadTester(
        # 负载类型
        workload_type='云到边',
        workload_load_directory='workloads',
        # 负载生成时间/负载所在文件夹
        workload_generated_time='2021-01-06 18-37-03 mix',
        # 需要运行的算法名称
        scheduling_algorithms=['ep', 'lrp', 'mrp', 'bra'],
        # 重复运行的次数，当前为重复运行一种算法repeat_times之后再运行下一算法
        repeat_times=5,
        metrics_server_base_url='http://localhost:8001/apis/metrics.k8s.io/v1beta1',
        # 总结的保存位置
        result_dir='results',
    )
    start = time.time()
    workload_tester.run()
    end = time.time()
    print("Total running time: %s seconds" % (end - start))

    draw_job_figures('results/jobs', 'results/figures', show_figure=False)
