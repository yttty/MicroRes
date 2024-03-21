import math
import operator
from typing import List, Tuple, Dict

import numpy as np
from sklearn.decomposition import PCA

from .model.distance import similarity
from .utils.wrapper import MetricWrapper
from .utils.logger import setupLogging


class MicroRes:
    """
    Core module of MicroRes
    """

    def __init__(self, f_cont, index_scaling=0.1):
        """
        f_cont: contribution function
        """
        self.logger = setupLogging("logs", "MicroRes", "full")
        self.f_cont = f_cont
        self.index_scaling = index_scaling

    def _maxContribution(self, mw, m):
        m_l = list(m)
        normal, faulty = mw.filterRt(m_l)
        d = np.abs(normal - faulty)
        dbar_t = d.transpose() - d.mean(axis=1)

        pca = PCA(n_components=1)
        delta_pc1 = pca.fit_transform(dbar_t).transpose()[0]

        # list of contribution values
        cont_l = []
        for i in range(dbar_t.shape[1]):
            cont_l.append((self.f_cont(dbar_t[:, i], delta_pc1), m_l[i]))

        cont_l.sort(key=operator.itemgetter(0), reverse=True)
        return cont_l[0]

    def _resIndexing(self, l, metricMetadata):
        dp = 0
        db = 0
        for idx, cm in enumerate(l):
            c, m = cm
            if metricMetadata[m] == "p":
                dp += c / (math.log2(idx + 2))  # rank = idx + 1
            else:
                db += c / (math.log2(idx + 2))
        r = 1 / (1 + math.exp((db - dp) * self.index_scaling))
        return r

    def eval(self,
             testId: str,
             metricMetadata: Dict,
             normalInterval: List[Tuple],
             faultyInterval: List[Tuple],
             metrics: np.ndarray):
        """
        Interface for evaluating the critical metrics
        """
        # load data wrapper
        mw = MetricWrapper(testId, metricMetadata,
                           normalInterval, faultyInterval, metrics)

        l = []
        m = set(metricMetadata.keys())

        while len(m) != 0:
            cmax, mimax = self._maxContribution(mw, m)
            l.append((cmax, mimax))
            m.remove(mimax)

        r = self._resIndexing(l, metricMetadata)

        return r
