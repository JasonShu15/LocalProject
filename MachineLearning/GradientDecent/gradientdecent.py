#coding:utf-8
import numpy as np

# Size of the points dataset.
m = 20
# Points x-coordinate and dummy value (x0, x1).
X0 = np.ones((m, 1))#注意写法,如果写成np.ones(m, 1)会报错
'''
arange:创建一维数组，左闭右开
reshape：改变数组的行列数,之前是一维数组,现在是20行1列，注意20行1列的写法
[[1][2][3][4][5][6][7][8][9][10][11][12][13][14][15][16][17][18][19][20]]中间没有逗号，加了逗号就变成list
'''
X1 = np.arange(1, m+1).reshape(m, 1)
'''
hstack,将两个数组合并,hstack是竖着合并，也就是增加列,vstack是横着合并，增加行
合并后的数组，其类型是根据原数组中小数点更多的那个保持一致,合并后的数据为20行2列
[[1. 1.] [1. 2.] [1. 3.] [1. 4.] [1. 5.] [1. 6.] [1. 7.] [1. 8.] [1. 9.] [1. 10.]
 [1. 11.][1. 12.][1. 13.][1. 14.][1. 15.][1. 16.][1. 17.][1. 18.][1. 19.][1. 20.]]
'''
X = np.hstack((X0, X1))

# Points y-coordinate
y = np.array([
    3, 4, 5, 5, 2, 4, 7, 8, 11, 8, 12,
    11, 13, 13, 16, 17, 18, 17, 19, 21
]).reshape(m, 1)  # y变成20行1列

# The Learning Rate alpha.
alpha = 0.01  #学习率 也称为步长


def error_function(theta, X, y):
    '''Error function J definition.'''
    '''
    1.numpy.dot向量的乘法(而不是矩阵的乘法),所以x和theta无论谁在前谁在后,是一样的
    3.numpy官网的示例
    >>> np.dot([2j, 3j], [2j, 3j])
        (-13+0j)
    '''
    diff = np.dot(X, theta) - y
    '''
    1.乘号和除号的优先级一样，并且没有带括号，因此这里就是表示m/2，带1.是因为需要返回值是小数
      如果不带，3/2的结果是1而不是1.5
    2.transpose:比较难理解,看csdn的理解https://blog.csdn.net/Hearthougan/article/details/72626643?locationNum=7&fps=1
      其实就是转置
    '''
    return (1./2*m) * np.dot(np.transpose(diff), diff)


def gradient_function(theta, X, y):
    '''Gradient of the function J definition.'''
    diff = np.dot(X, theta) - y
    return (1./m) * np.dot(np.transpose(X), diff)


def gradient_descent(X, y, alpha):
    '''Perform gradient descent.'''
    theta = np.array([1, 1]).reshape(2, 1)  # theta:[[1][1]]
    gradient = gradient_function(theta, X, y) # 1/m *(theta * X -y)
    '''
    1.absolute：求绝对值
    2.np.all:测试沿给定轴的所有数组元素是否都计算为True
    这句话可以理解为不是所有的np.absolute(gradient) <= 1e-5都满足时，执行后面的语句
    也就是说，当所有的np.absolute(gradient) <= 1e-5都满足时，while就不执行  
    '''
    while not np.all(np.absolute(gradient) <= 1e-5):
        theta = theta - alpha * gradient
        gradient = gradient_function(theta, X, y)
    return theta


optimal = gradient_descent(X, y, alpha)
print('optimal:', optimal)
print('error function:', error_function(optimal, X, y)[0, 0])
