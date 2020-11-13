#!/usr/bin/python

import argparse
import math
import time
from multiprocessing import Process
from multiprocessing import cpu_count

import requests

DEFAULT_SERVER_URL = 'http://localhost:80'
ITER_COUNT = int(2e3)
MB = 1024 ** 2


# CPU
def compute(iter_count):
    num = 0

    for i in range(1, iter_count + 1):
        num += 1 / (i * i)

    pi = math.sqrt(num * 6)


# IO
def io(size_mb: float):
    with open('/tmp/writen-io.txt', 'w') as f:
        size_128_mb = int(size_mb / 128)
        size_left_mb = size_mb % 128
        if size_128_mb:
            data = '1' * 128 * MB
            for _ in range(size_128_mb):
                f.write(data)
        f.write('1' * int(size_left_mb * MB))


# Network
def network(server_url: str, send_size_mb: int):
    port = server_url.split(':')[-1]
    if is_server_mode(server_url):
        print('以服务器模式启动，端口%s' % port)
        start_listen(server_url)
    elif send_size_mb > 0:
        print('以客户端模式启动，连接至{}，发送{}MB'.format(server_url, send_size_mb))
        connect_and_send(server_url, send_size_mb)


def is_server_mode(server_url: str):
    return server_url == DEFAULT_SERVER_URL


def connect_and_send(server_url: str, size_mb: float):
    requests.post(server_url, str_size_of(size_mb))


def start_listen(server_url: str):
    pass


def str_size_of(size_mb: float):
    return '1' * int(size_mb * MB)


def main():
    start_time = time.time()
    parse = argparse.ArgumentParser(description='running')
    parse.add_argument(
        "-c",
        "--cpu-count",
        default=0,
        type=int,
        help='指定cpu核数（<=0则为CPU超线程数）'
    )
    parse.add_argument(
        "-m",
        "--memory-mb",
        default=0,
        type=float,
        help='内存占用（MB），默认不占用'
    )
    parse.add_argument(
        "--iter-factor",
        default=1,
        type=float,
        help='程序工作量（迭代次数）* %d' % ITER_COUNT
    )
    parse.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        type=str,
        help='服务端的URL（默认情况下自身为服务端）'
    )
    parse.add_argument(
        "--send-size-mb",
        default=0,
        type=float,
        help='发送的文件大小（MB），默认情况下不发送'
    )
    parse.add_argument(
        "--write-size-mb",
        default=0,
        type=float,
        help='写入硬盘的大小（MB），默认不写入'
    )

    args = parse.parse_args()

    cpu_logical_count = int(args.cpu_count)
    if cpu_logical_count <= 0:
        cpu_logical_count = cpu_count()

    iter_count = int(args.iter_factor * ITER_COUNT)
    memory_used_mb = max(float(args.memory_mb), 0)
    server_url = str(args.server_url)
    send_size_mb = max(float(args.send_size_mb), 0)
    write_size_mb = max(float(args.write_size_mb), 0)

    try:
        ps_list = []

        # CPU
        print('占用CPU核数：{}'.format(cpu_logical_count))
        print('计算迭代次数：{} * {} = {}'.format(args.iter_factor, ITER_COUNT, iter_count))
        for i in range(0, cpu_logical_count):
            ps_list.append(Process(target=compute, args=(iter_count,), name='CPU-%d' % i))

        # Network TODO: 实现
        # ps_list.append(Process(target=network, args=(server_url, send_size_mb, ), name='Network'))

        # IO
        if write_size_mb > 0:
            print('预计磁盘写入大小：{}MB'.format(write_size_mb))
            ps_list.append(Process(target=io, args=(write_size_mb, ), name='IO'))

        # Memory
        if memory_used_mb > 0:
            print('预计内存占用：{}MB'.format(memory_used_mb))
            s = str_size_of(memory_used_mb)

        for p in ps_list:
            p.start()

        print('进程启动完毕，共启动{}个进程：{}'.format(len(ps_list), [p.name for p in ps_list]))

        for p in ps_list:
            p.join()

    except MemoryError:
        print("内存分配失败")

    finally:
        print("所有进程运行结束")
        print('使用时间：', round((time.time() - start_time) * 1000), 'ms')


if __name__ == "__main__":
    main()
