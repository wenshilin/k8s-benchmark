import abc


# evaluation summarizer interface
class EvaluationSummarizer(object):

    @abc.abstractmethod
    def write_summary(self, summary_name: str = None):
        pass
