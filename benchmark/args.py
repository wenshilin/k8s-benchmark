import argparse


def return_args():
    parser = argparse.ArgumentParser(
        description="Kubernetes-benchmark"
    )
    parser.add_argument(
        "--env",
        type=str,
        help="environment name"
    )
    parser.add_argument(
        '--sim-node-conf',
        type=str,
        help='Node configuration in simulation'
    )
    parser.add_argument(
        '--sim-base-url',
        type=str,
        default='http://localhost:8001',
        help='Simulation environment url'
    )
    parser.add_argument(
        '--result-dir',
        type=str,
        default='results',
        help='Result save directory'
    )
    parser.add_argument(
        '--workload-type',
        type=str,
        help='Workload type'
    )
    parser.add_argument(
        '--workload-base-dir',
        type=str,
        help='Workload load basic directory'
    )
    parser.add_argument(
        '--workload-dir',
        type=str,
        help='Workload directory'
    )
    parser.add_argument(
        '--metrics-server-base-url',
        type=str,
        default='http://localhost:8001/apis/metrics.k8s.io/v1beta1',
        help='Metrics server URL'
    )
    parser.add_argument(
        '--repeat-times',
        type=int,
        help='Repeat times'
    )
    parser.add_argument(
        '--schedulers',
        nargs='+',
        type=str
    )

    return parser.parse_args()
