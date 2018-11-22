#coding:utf-8
"""
-------------------------   算法库   -------------------------
Version  0.1.0


算法添加时，需安以下规则，并注明算法添加人
+===========================================================+
规则说明：
X: 特征，pandas.DataFrame, pandas.Series
y: 标签，pandas.DataFrame, pandas.Series
params: 参数，字典格式{参数名1: 参数值1, 参数名2: 参数值2}
fit方法 返回算法模型
predict方法 输入模型，返回预测数据numpy.array 或 pandas.Series
+===========================================================+

"""
import os

root_path = os.path.dirname(os.path.abspath(__file__))

# 新增方法需要写到alg_list里
alg_list = ['BPN']


class BPN(object):
    """
    X: 输入气象数据
    y: 理论功率
    rate: 限电比列
    Returns: 预测实际功率
    """

    def __init__(self):
        self.__author__ = 'Liu Sibo'

    def fit(self, x, y, params):
        from pybrain.datasets import SupervisedDataSet
        from pybrain.tools.shortcuts import buildNetwork
        from pybrain.supervised.trainers import BackpropTrainer
        from pybrain.structure import TanhLayer, LinearLayer
        from sklearn.preprocessing import MinMaxScaler
        '''
        进行归一化，将特征X和标签y都归一化到同一维度上
        '''
        scale_x = MinMaxScaler().fit(x.values.reshape(x.shape[0], -1))
        x_min_max = scale_x.transform(x.values.reshape(x.shape[0], -1))
        scale_y = MinMaxScaler().fit(y.values.reshape(y.shape[0], -1))
        y_min_max = scale_y.transform(y.values.reshape(y.shape[0], -1))

        num = x.shape[0]
        x_dim = x.shape[1]
        try:
            y_dim = y.shape[1]
        except:
            y_dim = 1
        model = buildNetwork(x_dim, 4, 16, y_dim, bias=True, hiddenclass=TanhLayer, outclass=LinearLayer)
        data_set = SupervisedDataSet(x_dim, y_dim)
        for i in range(num):
            data_set.addSample(x_min_max[i], y_min_max[i])
        train, test = data_set.splitWithProportion(0.99)
        trainer = BackpropTrainer(model, dataset=train, learningrate=0.02, lrdecay=1.0, momentum=0, verbose=True)
        trainingErrors, validationErrors = trainer.trainUntilConvergence(maxEpochs=15)
        model.dims = (x_dim, y_dim)
        model.scale_x = scale_x
        model.scale_y = scale_y
        return model

    def predict(self, x_predict, model):
        import numpy as np
        from pybrain.datasets import SupervisedDataSet
        x_min_max = model.scaler_x.transform(x_predict.values.reshape(x_predict.shape[0], -1))
        x_dim, y_dim = model.dims
        num = len(x_predict)
        tar = np.zeros((len(x_min_max), y_dim))
        data_set = SupervisedDataSet(x_dim, y_dim)
        for i in range(num):
            data_set.addSample(x_min_max[i], tar[i])
        output = model.activateOnDataset(data_set)
        y_inverse = model.scaler_y.inverse_transform(output.reshape(output.shape[0], -1))
        return y_inverse


