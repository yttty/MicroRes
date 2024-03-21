import logging
from typing import List

from scipy.stats import pearsonr, spearmanr, kendalltau
import numpy as np

logger = logging.getLogger("MicroRes")


class Euclidean:

    @staticmethod
    def eucl(ts_a, ts_b):  # T
        return np.sqrt(np.square(ts_a - ts_b).sum())


class ComplexityInvariantDistance:

    @staticmethod
    def cid_distance(ts_a, ts_b):  # [n_feat, T]
        ce_a = np.sqrt(np.sum(np.square(np.diff(ts_a))) + 1e-9)
        ce_b = np.sqrt(np.sum(np.square(np.diff(ts_b))) + 1e-9)
        d = np.sqrt(np.sum(np.square(ts_a - ts_b))) * \
            np.divide(np.maximum(ce_a, ce_b), np.minimum(ce_a, ce_b))
        return np.sum(d)


class DTW:

    @staticmethod
    def naive_dtw_distance(ts_a, ts_b, mww=5, d=lambda x, y: abs(x - y)**2):
        """Computes dtw distance between two time series

        Args:
            ts_a: time series a
            ts_b: time series b

        Returns:
            dtw distance
        """

        # Create cost matrix via broadcasting with large int
        # ts_a, ts_b = np.array(ts_a), np.array(ts_b)
        M, N = len(ts_a), len(ts_b)
        cost = np.full((M, N), np.inf)

        # Initialize the first row and column
        cost[0, 0] = d(ts_a[0], ts_b[0])
        for i in range(1, M):
            cost[i, 0] = cost[i - 1, 0] + d(ts_a[i], ts_b[0])

        for j in range(1, N):
            cost[0, j] = cost[0, j - 1] + d(ts_a[0], ts_b[j])

        # Populate rest of cost matrix within window
        for i in range(1, M):
            for j in range(max(1, i - mww), min(N, i + mww)):
                choices = cost[i - 1, j - 1], cost[i, j - 1], cost[i - 1, j]
                cost[i, j] = min(choices) + d(ts_a[i], ts_b[j])

        # Return DTW distance given window
        # print(cost)
        return cost[-1, -1]


class Correlation:

    @staticmethod
    def pearson(ts_a, ts_b):
        """Computes pearson correlation between two time series

        Args:
            ts_a: time series a
            ts_b: time series b

        Returns:
            r: correlation of a and b
            p: p value
        """
        # ts_a, ts_b = np.array(ts_a), np.array(ts_b)
        r, p = pearsonr(ts_a, ts_b)
        return r

    @staticmethod
    def spearman(ts_a, ts_b):
        """Computes spearman correlation between two time series

        Args:
            ts_a: time series a
            ts_b: time series b

        Returns:
            r: correlation of a and b
            p: p value
        """
        # ts_a, ts_b = np.array(ts_a), np.array(ts_b)
        r, p = spearmanr(ts_a, ts_b)
        return r

    @staticmethod
    def kendall(ts_a, ts_b):
        """Computes kendall correlation between two time series

        Args:
            ts_a: time series a
            ts_b: time series b

        Returns:
            r: correlation of a and b
            p: p value
        """
        # ts_a, ts_b = np.array(ts_a), np.array(ts_b)
        r, p = kendalltau(ts_a, ts_b)
        return r
