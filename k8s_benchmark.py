import logging
import os

from benchmark.args import return_args
from benchmark.figures.figures import draw_job_figures
from benchmark.workload_tester import RealEnvWorkloadTester
from benchmark.workload_tester import SimEnvWorkloadTester
from common.utils import kube_config


def main():
    args = return_args()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s'
    )
    kube_config.load_kube_config(args.kube_config_file)
    print(vars(args))

    env_type = args.env
    args_dict = vars(args)
    del args_dict['env']
    del args_dict['kube_config_file']
    if env_type == 'real':
        del args_dict['sim_node_conf']
        del args_dict['sim_base_url']
        tester = RealEnvWorkloadTester(**args_dict)
    else:
        del args_dict['metrics_server_base_url']
        tester = SimEnvWorkloadTester(**args_dict)

    tester.run()
    draw_job_figures(
        root_dir=os.path.join(args.result_dir, 'jobs'),
        save_dir=os.path.join(args.result_dir, 'figures'),
        show_figure=False
    )


if __name__ == '__main__':
    main()
