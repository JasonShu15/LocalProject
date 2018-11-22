#__author__ = '31215'
#coding:utf-8

from scipy import interpolate
import pandas as pd
import sys
path = "C:\libsvm-3.23\python"
sys.path.append(path)
from svmutil import *
import matplotlib.pyplot as plt
from Evaluate_method import *
from WindFarm import WindFarm as wf


def normalize(values, min, max):
    qxvalues = (values-min)/(max-min)
    return qxvalues


def time_seg(data, nh):
    num=24/nh
    Data = {}
    for i in range(num):
        tim_beg = (i*nh)
        tim_end = ((i+1)*nh)
        Data[i] = data[(data.index.hour >= tim_beg)&(data.index.hour < tim_end)]
    return Data


def point_err(outp, inp):
    abs_grades = []
    for i in range(len(inp)):
        if inp[i] != 0:
            abserr = abs(outp[i]-inp[i])/inp[i]

            if abserr > 0.25:
                absgrade = (abserr-0.25)*inp[i]*0.25*0.5/10000
            else:absgrade = 0
        else:
            abserr = abs(outp[i]-inp[i])
            absgrade = abserr*0.25*0.5/10000
        abs_grades.append(absgrade)
    return np.sum(abs_grades)


def svm_model_train (qx,labels,minspeed,maxspeed,minD,maxD,Cap):
    X = []
    speed = normalize(qx.iloc[:,0],minspeed,maxspeed).values * rate[0]
    direction = normalize(qx.iloc[:,1],minD,maxD).values * rate[1]

    Y = list(normalize(labels, 0, Cap).values)

    for n in range(speed.size):
        X.append(list([float(speed[n]), float(direction[n])]))
    param = '-s 3 -c 10 -g 10 -p 0.002'
    print type(X)
    # print X
    model = svm_train(Y,X,param)
    return model


def svm_model_predict(qx,labels,minspeed,maxspeed,minD,maxD,Cap,modeldata,model):
    X = []
    speed = normalize(qx.iloc[:,0],minspeed,maxspeed).values*rate[0]
    direction = normalize(qx.iloc[:,1],minD,maxD).values* rate[1]
    for n in range(speed.size):
        X.append(list([float(speed[n]), float(direction[n])]))

    y = [0] * len(X)
    pre, acc, val = svm_predict(y, X, model)
    pre_power = []
    for prepower in pre:
        pre_power.append(prepower*Cap)

    modeldata['preds'] = pre_power

    #plot
    plt.figure(3)
    plt.plot(qx.iloc[:, 0], labels, 'og')
    plt.plot(qx.iloc[:, 0], pre_power, 'ok')
    plt.show()

    plt.figure(4)
    plt.plot(labels.values, 'r')
    plt.plot(pre_power)
    plt.show()

    print "RMSE=%s"%(RMSE(pre_power, labels)/Cap)


class LineBuilder:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        print('click', event)
        if event.inaxes != self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        plotdata = pd.DataFrame(dict(inputs=self.xs, outputs=self.ys))
        plotdata.to_csv("c.csv")


if __name__ == '__main__':

    cid = 'JXLYM_360428'
    wth = 'MIX'
    stn_id = '001'
    start, end = '2018-10-11', '2019-09-31'
    Cap = 97500
    fm = wf(cid)

    modeldata = fm.get_merge_data(wth_source=wth, obs_source='exportdb', stn_id=stn_id,
                                  start_time=start, end_time=end, feature=['speed', 'direction'])
    modeldata = modeldata.set_index('ptime')

    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    ax.plot(modeldata['speed'].values, modeldata['power'].values, '.')
    line, = ax.plot([0], [0])  # empty line
    linebuilder = LineBuilder(line)
    plt.show()

    datas = pd.read_csv("c.csv")

    x, y = datas['inputs'].values, datas['outputs'].values
    f = interpolate.interp1d(x, y, kind='linear')

    newx = np.linspace(0, np.max(x), len(modeldata))
    newy = f(newx)

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111)
    ax2.plot(modeldata['speed'].values, modeldata['power'].values, '.')
    ax2.plot(newx, newy, '.')
    plt.show()

    rate = [1.0, 0.0001]   # wspd, direction
    # 归一化参数
    maxspeed = 25
    minspeed = 0
    maxD = 360
    minD = 0

    newdatas = pd.DataFrame(dict(newspeed=newx, newdire=np.linspace(0, 360, len(newx)), newpower=newy))
    qx = newdatas[['newspeed', 'newdire']]
    labels = newdatas['newpower']
    model = svm_model_train(qx, labels, minspeed, maxspeed, minD, maxD, Cap)

    qx_t = modeldata[['speed', 'direction']]
    labels_t = modeldata['power']
    svm_model_predict(qx_t, labels_t, minspeed, maxspeed, minD, maxD, Cap, modeldata, model)

    svm_save_model('model\\%s.mat'%cid, model)

