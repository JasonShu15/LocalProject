import numpy as np


def rmse(real, pred, cap = 49500):
    s = 1 - np.sqrt(np.square(real / 1000 - pred / 1000).sum()) / (cap / 1000 * np.sqrt(len(real)))
    return s


def harmonic(real, pred, cap = 49500):
    arr = abs(real / (real+pred) - 0.5) * abs(real - pred) / (sum(abs(real - pred)))
    e = 1.0 - 2.0 * arr.sum()
    return e


def normalize(values, min, max):
    qxvalues = (values-min)/(max-min)
    return qxvalues


def rev_normalize(norm_real, max, min):
    revalue = norm_real * (max - min) + min
    return revalue


