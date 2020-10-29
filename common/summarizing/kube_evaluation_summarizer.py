from .evaluation_summarizer import EvaluationSummarizer
from .job_summary_plugin import JobSummaryPlugin
from .pod_summary_plugin import PodSummaryPlugin
from .task_summary_plugin import TaskSummaryPlugin


class KubeEvaluationSummarizer(EvaluationSummarizer):

    def __init__(self):
        super().__init__()
        self.register_plugin(TaskSummaryPlugin())
        self.register_plugin(JobSummaryPlugin())
        self.register_plugin(PodSummaryPlugin())
