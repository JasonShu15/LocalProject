# -*- coding: utf-8 -*-
"""
@author: Haojie Shu
@time: 
@description:
"""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql://algorithm_write:algorithm0420@10.1.39.199:3306/exportdb?charset=utf8', echo=True)


df = pd.read_excel('D://Personal//Desktop//201805.xls')
indexes = df.index.tolist()
data = []
for i in indexes:
    rectime = df.iloc[i, 0]
    predict_wspd = df.iloc[i, 4]
    predict_power = float(df.iloc[i, 3]) * 1000
    wspd = df.iloc[i, 5]
    power = float(df.iloc[i, 2]) * 1000
    theorypower = ''
    power_dict = {'rectime': rectime, 'predict_wspd': predict_wspd, 'wspd': wspd, 'predict_power': predict_power, 'theorypower': theorypower, 'power': power}
    data.append(power_dict)
df = pd.DataFrame(data, columns=['rectime', 'predict_wspd', 'wspd', 'predict_power', 'theorypower', 'power'])

df.to_sql('factory_652244', engine, chunksize=500, if_exists='append', index=False)