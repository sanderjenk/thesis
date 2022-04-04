import numpy as np

from pymoo.indicators.hv import Hypervolume
from pymoo.util.misc import to_numpy
from pymoo.util.termination.sliding_window_termination import SlidingWindowTermination


class HVTermination(SlidingWindowTermination):

    def __init__(self,
                 n_last=20,
                 tol=1e-6,
                 nth_gen=1,
                 n_max_gen=None,
                 n_max_evals=None,
                 **kwargs):

        super().__init__(metric_window_size=n_last,
                         data_window_size=2,
                         min_data_for_metric=2,
                         nth_gen=nth_gen,
                         n_max_gen=n_max_gen,
                         n_max_evals=n_max_evals,
                         **kwargs)
        self.tol = tol

    def _store(self, algorithm):
        return algorithm.opt.get("F")

    def _metric(self, data):
        return Hypervolume([1.1, 1.1, 1.1]).do(data[-1])

    def _decide(self, metrics):
        return (to_numpy(metrics).max() - to_numpy(metrics).min())> self.tol