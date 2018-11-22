# -*- coding: utf-8 -*-
"""
@author: Haojie Shu
@time: 2018/11/21
@description:svm示例https://sadanand-singh.github.io/posts/svmpython/
"""
import numpy as np
from sklearn import svm, datasets
import matplotlib.pyplot as plt
iris = datasets.load_iris()
X = iris.data[:, :2]  # we only take the first two features.
y = iris.target
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
h = (x_max / x_min)/100

xa = np.arange(x_min, x_max, h)  # arange:生成一维数组, 三个参数分别为起始数、终止数和步数
xb = np.arange(y_min, y_max, h)
xx, yy = np.meshgrid(xa, xb)  # meshgrid: 生成网格型数据,见官网说明

X_plot = np.c_[xx.ravel(), yy.ravel()]  # c_:按行连接两个矩阵,把两矩阵左右相加, ravel: 多维矩阵变为一维
C = 1.0  # SVM regularization parameter

svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(X, y)
Z = svc.predict(X_plot)
Z = Z.reshape(xx.shape)

plt.figure(figsize=(15, 5))
plt.subplot(121)
plt.contourf(xx, yy, Z, cmap=plt.cm.tab10, alpha=0.3)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Set1)
plt.xlabel('Sepal length')
plt.ylabel('Sepal width')
plt.xlim(xx.min(), xx.max())
plt.title('SVC with linear kernel')

C = 1.0  # SVM regularization parameter
svc = svm.SVC(kernel='rbf', C=C, decision_function_shape='ovr').fit(X, y)

Z = svc.predict(X_plot)
Z = Z.reshape(xx.shape)

plt.subplot(122)
plt.contourf(xx, yy, Z, cmap=plt.cm.tab10, alpha=0.3)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Set1)
plt.xlabel('Sepal length')
plt.ylabel('Sepal width')
plt.xlim(xx.min(), xx.max())
plt.title('SVC with RBF kernel')

plt.show()