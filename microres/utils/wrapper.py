from typing import List, Tuple, Dict

import numpy as np


class MetricWrapper:
    """
    Wrapper class for metrics. It only deals with data splitting and dimension filtering.
    """

    def __init__(self,
                 testId: str,
                 metricMetadata: Dict,
                 normalInterval: List[Tuple],
                 faultyInterval: List[Tuple],
                 metrics: np.ndarray):
        """
        Params
        ------
            `testId`: the name of the test case
            `metricMetadata`: a list of the metrics' names and categories
            `faultyInterval`: intervals of faulty metrics
            `normalInterval`: intervals of normal metrics
            `metrics`: np.ndarray of metrics
        """

        self._testId = testId
        self._metricMetadata = metricMetadata
        self._metrics = metrics
        self._metricsCount = self._metrics.shape[0]
        self._faultyInterval = faultyInterval
        self._normalInterval = normalInterval
        self._normalMetrics, self._faultyMetrics = self._splitMetrics(
            self._normalInterval, self._faultyInterval, self._metrics)
        assert self._normalMetrics.shape[1] == self._faultyMetrics.shape[1], "Normal and faulty length must be equal"
        # Map<name, dim_idx>
        self._name2dimension = dict(
            map(lambda x: (x[1], x[0]), enumerate(self._metricMetadata)))

    def _splitMetrics(self, normalInterval, faultyInterval, metrics):
        normalMetrics = None
        for interval in normalInterval:
            tmp = metrics[..., interval[0]:interval[1]]
            if normalMetrics is not None:
                normalMetrics = np.hstack((normalMetrics, tmp))
            else:
                normalMetrics = tmp

        faultyMetrics = None
        for interval in faultyInterval:
            tmp = metrics[..., interval[0]:interval[1]]
            if faultyMetrics is not None:
                faultyMetrics = np.hstack((faultyMetrics, tmp))
            else:
                faultyMetrics = tmp

        return normalMetrics, faultyMetrics

    def _getRetainedIdx(self, removedIdx):
        retainedIdx = list(range(self._metricsCount))
        for idx in removedIdx:
            retainedIdx.remove(idx)
        return retainedIdx

    def filterRm(self, removedMetricNames: List[str] = []):
        """
        Get normal and faulty metrics after removing some metrics

        Params
        ------
            removedMetricNames: list of metric names to remove

        Returns
        ------
            normal, faulty: two ndarrays of normal and faulty metrics with specified dimensions
        """
        # Throw exception if the metric name is not found
        removedIdx = [self._name2dimension[name]
                      for name in removedMetricNames]

        # convert removed idx to retained idx
        retainedIdx = self._getRetainedIdx(removedIdx)

        if len(retainedIdx) == 0:
            raise ValueError('Cannot remove all metrics')

        # slice the np.ndarray
        normal = self._normalMetrics[retainedIdx, :]
        faulty = self._faultyMetrics[retainedIdx, :]

        return normal, faulty

    def filterRt(self, retainedMetricNames: List[str] = []):
        """
        Get normal and faulty metrics after reatining some metrics

        Params
        ------
            retainedMetricNames: list of metric names to retain

        Returns
        ------
            normal, faulty: two ndarrays of normal and faulty metrics with specified dimensions
        """
        if len(retainedMetricNames) == 0:
            raise ValueError('Must retain at least one metric')

        # Throw exception if the metric name is not found
        retainedIdx = [self._name2dimension[name]
                       for name in retainedMetricNames]

        # slice the np.ndarray
        normal = self._normalMetrics[retainedIdx, :]
        faulty = self._faultyMetrics[retainedIdx, :]

        return normal, faulty


if __name__ == "__main__":
    # sample data structure
    testId = 'aaabbb'
    metricMetadata = {
        'metric1': 'b',
        'metric2': 'p',
        'metric3': 'p'
    }
    normalInterval = [(0, 50), (100, 120)]
    faultyInterval = [(50, 100), (150, 170)]
    metrics = np.random.normal(size=(3, 200))

    # test apis
    mw = MetricWrapper(testId, metricMetadata,
                       normalInterval, faultyInterval, metrics)
    normal, faulty = mw.filterRm(removedMetricNames=['metric1'])
    assert normal.shape == faulty.shape
