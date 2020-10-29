from typing import *

from .summary_plugin import SummaryPlugin


class EvaluationSummarizer(object):

    def __init__(self):
        self.summary_plugins: List[SummaryPlugin] = []

    def register_plugin(self, plugin: SummaryPlugin):
        self.summary_plugins.append(plugin)

    def write_summary(self, pods, now, summary_name: str):
        for plugin in self.summary_plugins:
            plugin.write_summary(pods, now, summary_name)
