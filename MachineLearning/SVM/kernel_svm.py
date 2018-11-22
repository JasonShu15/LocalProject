# -*- coding: utf-8 -*-
"""
@author: Haojie Shu
@time: 2018/09/28
@description:含核函数的SVM算法,也即二维空间不可分,只能在高维空间中分
"""
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import numpy as np

X, y = datasets.make_moons(noise=0.15, random_state=666)  # 使用半月形数据并加入噪音

plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()


def rbf_kernel_svc(gamma):  # 对数据进行预处理
    """
    Pipeline(steps:list,memory=None)
    第一个参数steps里面的list元素是Tuple
    """
    return Pipeline(steps=[("std_scaler", StandardScaler()), ("svc", SVC(kernel="rbf", gamma=gamma))])


svc = rbf_kernel_svc(gamma=1)
svc.fit(X, y)


def plot_decision_boundary(model, axis):  # 添加绘制图像函数

    x0, x1 = np.meshgrid(
        np.linspace(axis[0], axis[1], int((axis[1]-axis[0])*100)).reshape(-1, 1),
        np.linspace(axis[2], axis[3], int((axis[3]-axis[2])*100)).reshape(-1, 1),
    )
    x_new = np.c_[x0.ravel(), x1.ravel()]

    y_predict = model.predict(x_new)
    zz = y_predict.reshape(x0.shape)

    from matplotlib.colors import ListedColormap
    custom_map = ListedColormap(['#EF9A9A', '#FFF59D', '#90CAF9'])

    plt.contourf(x0, x1, zz, linewidth=5, cmap=custom_map)


plot_decision_boundary(svc, axis=[-1.5, 2.5, -1.0, 1.5])
plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()  # gamma=1

svc_gamma100 = rbf_kernel_svc(gamma=100)
svc_gamma100.fit(X, y)

plot_decision_boundary(svc_gamma100, axis=[-1.5, 2.5, -1.0, 1.5])
plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()  # gamma=100, 此时高斯分布越窄, 有点过拟合


svc_gamma10 = rbf_kernel_svc(gamma=10)
svc_gamma10.fit(X, y)

plot_decision_boundary(svc_gamma10, axis=[-1.5, 2.5, -1.0, 1.5])
plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()  # gamma=10

svc_gamma10 = rbf_kernel_svc(gamma=0.5)
svc_gamma10.fit(X, y)

plot_decision_boundary(svc_gamma10, axis=[-1.5, 2.5, -1.0, 1.5])
plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()  # gamma=0.5


svc_gamma10 = rbf_kernel_svc(gamma=0.1)  # gamma传入0.1
svc_gamma10.fit(X, y)

plot_decision_boundary(svc_gamma10, axis=[-1.5, 2.5, -1.0, 1.5])
plt.scatter(X[y == 0, 0], X[y == 0, 1])
plt.scatter(X[y == 1, 0], X[y == 1, 1])
plt.show()  # gamma=0.1,决策边界和一个线性的决策边界差不多，欠拟合