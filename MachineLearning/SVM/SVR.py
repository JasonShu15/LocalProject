# -*- coding: utf-8 -*-
"""
@author: Haojie Shu
@time: 2018/11/21
@description:SVR算法的实际运用https://sadanand-singh.github.io/posts/svmpython/
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
# numpy.random.rand:制造(0,1)之间的随机数,200和1表示行列数.sort: 进行排序
X = np.sort(5 * np.random.rand(200, 1), axis=0)
y = np.sin(X).ravel()  # ravel: 将多维数组变为一维
'''
1.当只有一个参数是表示一维数组，里面的40表示数组中元素的个数
2.为了理解这个表达式,可以设a=y[::5]
  那么 a+= 3*(0.5 - np.random.rand(40)),则有 a=a+3*(0.5 - np.random.rand(40))
  a=y[::5]+3*(0.5 - np.random.rand(40)),y[::5]相当于对y隔5个点取数,最后再执行 y[::5]=a
  最后,这个地方其实可以简单理解为在0,5,10,15....的位置执行加操作,其他位置不执行加操作
'''
y[::5] += 3 * (0.5 - np.random.rand(40))
'''
1.在SVR中,要做的是找到一个超平面，使得所有数据到这个超平面的距离最小
2.当kernel是linear的时候,相当于将所有的点投影到高维空间,为了便于理解,这里认为高维空间就是三维空间, 然后找到一个平面
  这个平面可以使得所有投影后的点到这个平面的距离和最小,再将这个平面投影回二维空间,就是我们看到的决策边界
3.C是惩罚系数,就是说你对误差的宽容度,这个值越高,说明你越不能容忍出现误差,C的默认值是1
'''
svr_lin = SVR(kernel='linear', C=10000)
y_lin = svr_lin.fit(X, y).predict(X)
# scatter函数中的x和y要么形状完全相同,要么二者的行列数刚好相反,例如x的行数为4行3列,y的行数为3行4列时,也可以绘制散点图
plt.scatter(X, y_lin, color='navy')
plt.show()

'''
1.当kernel是rbf的时候,得到的决策边界是非线性的,在SVR中kernel的值默认是rbf
2.gamma是选择rbf作为kernel后,该函数自带的一个参数,隐含地决定了数据映射到新的特征空间后的分布
             gamma值越小,模型复杂度越低
             gamma值越大,模型复杂度越高
  gamma的默认值是1/n_feature
'''
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
y_rbf = svr_rbf.fit(X, y).predict(X)
plt.scatter(X, y_rbf, color='red')
plt.show()

svr_poly = SVR(kernel='poly', C=1e3, degree=3)
y_poly = svr_poly.fit(X, y).predict(X)
plt.scatter(X, y_poly, color='green')
plt.show()
