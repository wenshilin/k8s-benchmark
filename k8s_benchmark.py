import os

from benchmark.args import return_args
from benchmark.figures.figures import draw_job_figures
from benchmark.workload_tester import RealEnvWorkloadTester
from benchmark.workload_tester import SimEnvWorkloadTester


def main():
    args = return_args()
    print(vars(args))

    env_type = args.env
    args_dict = vars(args)
    del args_dict['env']
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
