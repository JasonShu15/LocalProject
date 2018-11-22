#coding:utf-8
from Utils.examine import *
import pandas as pd
import os


def filter_tolerate_old(data, cap):
    """
    数据过滤，通过实测功率和实测风速的对比，过滤掉限电较为严重的数据
    :param data: 气象与实测以时间合并的数据，列需包括'ptime', 'wspd', 'theorypower'
    :param cap:
    :param fig: 是否显示散点图
    :return: 过滤后的数据
    """

    df = data.copy()
    df.index = df['ptime']
    df = df.drop(['ptime'], axis=1)
    if 'wspd' in df.columns:
        # 定义权重系数
        weight = float(cap) / 49500
        tolerate = 5000 * weight

        # 按0.1的刻度，将0~26m/s的风速划分为260段（根据数据量，数据量少时应将刻度扩大）
        if len(df) < 3000:
            x = np.arange(0, 26, 0.4)
        elif len(df) < 6000:
            x = np.arange(0, 26, 0.3)
        elif len(df) < 9000:
            x = np.arange(0, 26, 0.2)
        else:
            x = np.arange(0, 26, 0.1)
        col = 'wspd'
    else:
        # # 定义权重系数
        # weight = float(cap) / 30000
        # tolerate = 3000 * weight
        #
        # if len(df) < 3000:
        #     x = np.arange(0, 1100, 15)
        # elif len(df) < 6000:
        #     x = np.arange(0, 1100, 10)
        # elif len(df) < 9000:
        #     x = np.arange(0, 1100, 7)
        # else:
        #     x = np.arange(0, 1100, 5)
        # col = 'radiation'
        return data
    curve = []
    filtered = pd.DataFrame()
    for i in range(len(x) - 1):
        delta = df[(df.loc[:, col] >= x[i]) & (df.loc[:, col] < x[i + 1])]
        delta = delta.sort_values('theorypower')
        # 取每段中数据的平均值及方差
        avg = delta['theorypower'].mean()
        std = delta['theorypower'].std()
        # 根据平均值±方差*1.5的区间，过滤离群值，某些区域限电较为严重，所以当方差过大时（大于5000*W），不过滤，以免滤除合理数据
        if std < 5000 * weight:
            delta = delta[(delta['theorypower'] < avg + 1.5 * std) & (delta['theorypower'] > avg - 1.5 * std)]
        if len(delta) > 3:
            # 取过滤后的2个最大值的平均作为该段数据的参考值
            delta_y = delta.loc[:, 'theorypower'].iloc[-2:].mean()
            delta_x = x[i]
            if len(curve) <= 2:
                curve.append([delta_x, delta_y])
            # 保证符合单调递增的趋势
            elif (len(curve) >= 2) & (delta_y >= curve[-1][-1] - tolerate * weight):
                curve.append([delta_x, delta_y])
                # 对参考值向下取保留值
                filtered = filtered.append(
                    delta[((delta_y - delta.loc[:, 'theorypower']) < tolerate) & ((delta_y - delta.loc[:, 'theorypower']) > 0)])

    filtered.insert(0, 'ptime', filtered.index)
    filtered.sort_values('ptime', inplace=True)
    filtered.reset_index(drop=True, inplace=True)
    # df_new = pd.merge(filtered['ptime'], data, on='ptime', how='left')
    return filtered


def filter_tolerate(data, cap):

    if 'wspd' in data.columns:
        df = data.copy()
        def func(speed, cap):
            return cap / (1 + 164 * np.exp(-0.6 * speed))

        tx = df['wspd'].values.copy()
        tx.sort()
        ty = func(tx, cap)
        noise = np.random.rand(len(tx)) * cap/20 - 0.5 * cap/20
        ty = ty + noise
        tho = pd.DataFrame(tx, columns=['speed'])
        tho.insert(1, 'power', ty)
        # tho = tho[(tho['power'] >= 0) & (tho['power'] < cap)]

        df = df.sort_values(['wspd']).reset_index(drop=True)
        df.loc[df['power'].values < tho['power'].values * 0.9, 'theorypower'] = \
            tho.loc[df['power'].values < tho['power'].values * 0.9, 'power']
        return df.sort_values(['ptime']).reset_index(drop=True)
    else:
        return filter_tolerate_old(data, cap)




def filter_fit(data, cap):
    from sklearn.svm import SVR
    """
    用svm拟合实测与功率，保留偏差在25%内的点
    :param data:气象与实测以时间合并的数据，列需包括'wspd', 'power'
    :param cap:
    :return:
    """
    df = data.copy()

    def std_model(qx, labels, cap, minspeed=0, maxspeed=25):
        x = normalize(qx, minspeed, maxspeed).values
        y = normalize(labels, 0, cap).values
        model = SVR(C=10, gamma=20)
        model.fit(x.reshape(-1, 1), y)
        pre = model.predict(x.reshape(-1, 1))
        pre_power = pre * cap
        return pre_power

    qx = df.loc[:, 'wspd']
    labels = df.loc[:, 'power']
    pre_power = std_model(qx, labels, cap, minspeed=0, maxspeed=25)
    error = abs(pre_power - labels)
    df['error'] = error
    Q1 = df['error'].quantile(q=0.25, interpolation='nearest')
    Q3 = df['error'].quantile(q=0.75, interpolation='nearest')
    IQR = Q3 - Q1
    Eup = Q3 + 1.50 * IQR
    df_fil = df[df['error'] < Eup]
    df_new = data.iloc[df_fil.index, :]
    df_new.reset_index(drop=True, inplace=True)
    return df_new


def filter_corr(data, cap):
    '''
    过滤掉预测与实测不相关时段的数据；
    按每2小时计算预测与实测的相关性，删除相关性为负，和数据偏差超过4m/s的数据
    :param data: 气象与实测以时间合并的数据
    :return:过滤后的数据
    '''
    speed_feature = filter(lambda x: x.count('speed') == 1, data.columns)  # 风字段名
    speed = speed_feature[0]
    def corr(d):
        if len(d)>2:
            if (np.corrcoef(d['wspd'], d[speed])[1][0] > 0)\
                    &(np.mean(abs(d['wspd'] - d[speed])) < 4):
                return 1
            else:
                return 0
        elif np.mean(abs(d['wspd'] - d[speed])) < 4:
            return 1
        else:
            return 0

    df = data.copy()
    df.index = df['ptime']
    df = df.drop(['ptime'], axis=1)
    positive = df.resample('1H')[['wspd',speed]].apply(corr)
    filtered = pd.DataFrame()
    for i in range(len(positive[positive == 1])):
        try:
            tmp = positive[positive == 1].index[i].strftime('%Y-%m-%d %H')
            filtered = filtered.append(df[tmp])
        except:
            print(i)
    filtered.insert(0, 'ptime', filtered.index)
    filtered.reset_index(drop=True, inplace=True)
    df_new = pd.merge(filtered[['ptime']], data, on='ptime', how='left')
    return df_new


def filter_wtc(data, cap):
    def func(speed, cap):
        return cap / (1 + 164 * np.exp(-0.6 * speed))

    df = data.copy()
    tx = df['wspd'].values.copy()
    tx.sort()
    ty = func(tx, cap)
    noise = np.random.rand(len(tx)) * cap/20 - 0.5 * cap/20
    ty = ty + noise
    tho = pd.DataFrame(tx, columns=['speed'])
    tho.insert(1, 'power', ty)
    # tho = tho[(tho['power'] >= 0) & (tho['power'] < cap)]

    df = df.sort_values(['wspd']).reset_index(drop=True)
    df.loc[df['power'].values < tho['power'].values * 0.9, 'power'] = \
        tho.loc[df['power'].values < tho['power'].values * 0.9, 'power']
    return df.sort_values(['ptime']).reset_index(drop=True)

def filter_k(data, cap):
    """根据最佳k值过滤数据"""
    in_df = data[data['power']>0].sort_values(by='wspd')
    out_df = data[data['power']>=cap*0.99].sort_values(by='wspd', ascending='False')
    in_wspd, out_wspd = in_df['wspd'].values[0], out_df['wspd'].values[0]
    start_full_index = out_df.index[0]
    data['k'] = data['power']/(data['wspd']**3)
    k=0
    while True and k<2000:
        k+=1
        #print k
        cut_df = data[data['k']>k]
        if start_full_index not in cut_df.index:
            break
    del cut_df['k']
    return cut_df

def filter_none(data, Cap):
    return data
