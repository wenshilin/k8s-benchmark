import datetime
import os

import plotly as py
import pytz

from benchmark.gantt import create_gantt_data, draw_gantt
from scripts.read_pod_from_file import read_pod_from_file


def main():
    pickle_filenames = [
        '2020-11-01 10-14-18-边到云到边-ds.pk'
    ]
    pickle_dir = 'results/pods'
    pickle_filenames = [os.path.join(pickle_dir, pf) for pf in pickle_filenames]
    gantt_data = []
    colors = {}
    default_colors = py.colors.DEFAULT_PLOTLY_COLORS
    benchmark = datetime.datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.timezone('UTC'))

    for idx, pf in enumerate(pickle_filenames):
        pods = read_pod_from_file(pf)
        scheduler_name = pf.split('-')[-1].split('.')[0]
        data = create_gantt_data(pods, scheduler_name)

        first_start_time = min([d['Start'] for d in data])
        for d in data:
            d['Start'] = d['Start'] - first_start_time + benchmark
            d['Finish'] = d['Finish'] - first_start_time + benchmark

        gantt_data.extend(data)
        colors[scheduler_name] = default_colors[idx % len(default_colors)]

    gantt_data.sort(key=lambda d: d['Task'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    draw_gantt(gantt_data, colors, now)


if __name__ == '__main__':
    main()
