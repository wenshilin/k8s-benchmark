import logging
import time
import warnings

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
        workload_type='边到云',
        workload_load_directory='workloads',
        # 负载生成时间/负载所在文件夹
        workload_generated_time='2020-12-08 00-28-35',
        # 需要运行的算法名称
        scheduling_algorithms=['ep', 'lrp', 'mrp', 'bra'],
        # 重复运行的次数，当前为重复运行一种算法repeat_times之后再运行下一算法
        repeat_times=10,
        metrics_server_base_url='http://localhost:8001/apis/metrics.k8s.io/v1beta1',
    )
    start = time.time()
    workload_tester.run()
    end = time.time()
    print("Total running time: %s seconds" % (end - start))
