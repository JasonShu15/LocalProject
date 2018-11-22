# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 14:02:27 2018

@author: PIAO
"""
import pandas as pd
import MySQLdb
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

def mysql_conn(db='filter_config'):
    user = 'algorithm_group'
    pwd = 'algorithm'
    ip = '10.1.39.199'
    port = 3306
    conn_modeling = MySQLdb.connect(host=ip, db=db, user=user, passwd=pwd ,port=port, charset='utf8')
    return conn_modeling

def create_table(table_name):
    conn = mysql_conn('filter_config')
    cursor=conn.cursor()
    table_drop =  "DROP TABLE IF EXISTS `{table_name}`".format(table_name=table_name)   
    table_create = "CREATE TABLE `{table_name}` (\
    `Num` INT DEFAULT NULL COMMENT '时间',\
    `speed_u` float(10,2) DEFAULT NULL COMMENT '风速上限',\
    `power_u` float(10,2) DEFAULT NULL COMMENT '功率上限',\
    `speed_d` float(10,2) DEFAULT NULL COMMENT '风速下限',\
    `power_d` float(10,2) DEFAULT NULL COMMENT '功率下限',\
    UNIQUE KEY `union_key` (`Num`) USING BTREE\
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;".format(table_name=table_name)   
    cursor.execute(table_drop)
    cursor.execute(table_create)
    cursor.close()
    conn.commit()
    conn.close()
    
def insert_filter_config(output,wfid):
    from sqlalchemy import create_engine 
    engine = create_engine('mysql://algorithm_group:algorithm@10.1.39.199:3306/filter_config?charset=utf8') 
    output.to_sql('%s'%wfid, engine,  chunksize=50000, index=False, if_exists='append') 
   

def get_windfarm_info(cid):
    conn = mysql_conn('WindFarmdb')
    windfarm_info = pd.read_sql("SELECT * FROM wind_farm_info where cid = '%s'" % cid, conn)
    conn.close()
    return windfarm_info

        
def filter_manual(data, cap, wfid):
    from scipy import interpolate
    
    conn = mysql_conn('filter_config')
    cursor = conn.cursor()
    sql =  "SELECT * FROM `{table_name}`".format(table_name=wfid)
    fl=pd.read_sql(sql,conn)
    cursor.close()
    conn.commit()
    conn.close()
    
    df = data.copy()
    indexs = list(df[np.isnan(df['wspd'])].index)
    df = df.drop(indexs)
    indexs = list(df[np.isnan(df['power'])].index)
    df = df.drop(indexs)
    wspd=df['wspd'].values
    wspd_max=np.max(wspd)
    if wspd_max>25: 
        u_add=np.linspace(25+10**-10,wspd_max,20)
        add_values = pd.DataFrame(columns = ["Num", "speed_u","power_u","speed_d","power_d"])
        add_values['speed_u'],add_values['speed_d']=u_add,u_add
        add_values['power_u'],add_values['power_d']=fl['power_u'][999],fl['power_d'][999]
        add_values['Num']=np.linspace(1001,1020,20)
        fl = fl.append(add_values,ignore_index=True)
    
    f_up = interpolate.interp1d(fl['speed_u'].values,fl['power_u'].values,kind='quadratic')
    f_down = interpolate.interp1d(fl['speed_d'].values,fl['power_d'].values,kind='quadratic')  
    df['up_power']=f_up(df['wspd'])
    df['down_power']=f_down(df['wspd'])
    df.loc[df['power'].values > df['up_power'].values, 'flag']=1
    df.loc[df['power'].values < df['down_power'].values, 'flag']=1
    df.loc[df['power'].values > df['up_power'].values, 'power']=(df['up_power']+df['down_power'])/2
    df.loc[df['power'].values < df['down_power'].values, 'power']=(df['up_power']+df['down_power'])/2
    del df['up_power'],df['down_power']
    
    return df

def filter_config(data, cap, wfid):
    from scipy import interpolate
    
    conn = mysql_conn('filter_config')
    cursor = conn.cursor()
    sql =  "SELECT * FROM `{table_name}`".format(table_name=wfid)
    fl=pd.read_sql(sql,conn)
    cursor.close()
    conn.commit()
    conn.close()
    
    df = data.copy()
    indexs = list(df[np.isnan(df['wspd'])].index)
    df = df.drop(indexs)
    indexs = list(df[np.isnan(df['power'])].index)
    df = df.drop(indexs)
    wspd=df['wspd'].values
    wspd_max=np.max(wspd)
    if wspd_max>25: 
        u_add=np.linspace(25+10**-10,wspd_max,20)
        add_values = pd.DataFrame(columns = ["Num", "speed_u","power_u","speed_d","power_d"])
        add_values['speed_u'],add_values['speed_d']=u_add,u_add
        add_values['power_u'],add_values['power_d']=fl['power_u'][999],fl['power_d'][999]
        add_values['Num']=np.linspace(1001,1020,20)
        fl = fl.append(add_values,ignore_index=True)
    
    f_up = interpolate.interp1d(fl['speed_u'],fl['power_u'],kind='quadratic')
    f_down = interpolate.interp1d(fl['speed_d'].values,fl['power_d'].values,kind='quadratic')  
    df['up_power']=f_up(df['wspd'])
    df['down_power']=f_down(df['wspd'])
    df.loc[df['power'].values > df['up_power'].values, 'flag']=1
    df.loc[df['power'].values < df['down_power'].values, 'flag']=1
    df = df[np.isnan(df['flag']) == True]
    del df['up_power'],df['down_power'],df['flag']
    
    return df,fl

def show_fig(input_data,filter_data,fl,model_data,cid,cap):
    
    special_data=model_data.loc[model_data['flag'].values ==1]

    cap_line = pd.DataFrame(columns = ["x", "y"])
    cap_line['x']=np.linspace(0,30,31)
    cap_line['y']=cap
        
    fig=plt.figure(1)
    ax = fig.add_subplot(111)  
    ax.grid(which= 'major')
    ax.set_title(str(cid)+'-'+str(cap)) 
    plt.sca(ax)
    #plt.ylim(0, cap*1.1)
    #plt.xlim(0, 25)
    plt.plot(input_data['wspd'].values,input_data['power'].values,'.')
    plt.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g')         
    plt.plot(fl['speed_u'], fl['power_u'], linestyle='-', color='r')        
    plt.plot(fl['speed_d'], fl['power_d'], linestyle='-', color='r')
    label=['Raw','Cap']
    plt.legend(label,loc=0) 
    plt.savefig(cid+'_'+'.jpg')
    plt.show()
    

    
    fig=plt.figure(2)
    ax = fig.add_subplot(111)  
    ax.grid(which= 'major')
    ax.set_title(str(cid)+'-'+str(cap)) 
    plt.sca(ax)
    #plt.ylim(0, cap*1.1)
    #plt.xlim(0, 25)
    plt.plot(filter_data['wspd'].values,filter_data['power'].values,'.')
    plt.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g')         
    plt.plot(fl['speed_u'], fl['power_u'], linestyle='-', color='r')        
    plt.plot(fl['speed_d'], fl['power_d'], linestyle='-', color='r')
    
    label=['Raw','Cap']
    plt.legend(label,loc=0) 
    plt.savefig(cid+'_'+'config'+'.jpg')
    plt.show()
    
    fig=plt.figure(3)
    ax = fig.add_subplot(111)  
    ax.grid(which= 'major')
    ax.set_title(str(cid)+'-'+str(cap)) 
    plt.sca(ax)
    #plt.ylim(0, cap*1.1)
    #plt.xlim(0, 25)
    plt.plot(filter_data['wspd'].values,filter_data['power'].values,'.')
    plt.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g')         
    plt.plot(fl['speed_u'], fl['power_u'], linestyle='-', color='r')        
    plt.plot(fl['speed_d'], fl['power_d'], linestyle='-', color='r')
    plt.plot(special_data['wspd'].values,special_data['power'].values,'.',color='k')
    
    label=['Raw','Cap']
    plt.legend(label,loc=0) 
    plt.savefig(cid+'_'+'manual'+'.jpg')
    plt.show()


 
    
class LineBuilder_up:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):

        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        plotdata = pd.DataFrame(dict(speed_u=self.xs,power_u=self.ys))
        plotdata.to_csv("select_up.csv")



class LineBuilder_down:
    def __init__(self, line):
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):

        if event.inaxes!=self.line.axes: return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
        plotdata = pd.DataFrame(dict(speed_d=self.xs,power_d=self.ys))
        plotdata.to_csv("select_down.csv")

def design_line(input_data, wfid, cap, cid, sname):

    print "Wait wait... Running!!!",wfid, sname
    cap_line = pd.DataFrame(columns = ["x", "y"])
    cap_line['x']=np.linspace(0,30,31)
    cap_line['y']=cap
    v_line = pd.DataFrame(columns = ["x", "y"])
    v_line['y']=np.linspace(0,cap*1.1,31)
    v_line['x']=(25)
    
    fig = plt.figure('up'+'_'+str(cap))
    ax = fig.add_subplot(111)
    ax.grid(which= 'major')
    plt.ylim(0, cap*1.1)
    plt.xlim(0, 30)
    ax.set_title('click to build up-limite line ')
    ax.plot(input_data['wspd'].values,input_data['power'].values,'.')       
    ax.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g')
    ax.plot(v_line['x'].values,v_line['y'].values,linestyle='-', color='g')        
    line, = ax.plot([0], [0])  
    data_limit_up = LineBuilder_up(line)
    plt.show()
        
    data_limit_up = pd.read_csv('select_up.csv')
    f_up = interpolate.interp1d(data_limit_up['speed_u'].values,data_limit_up['power_u'].values,kind='quadratic')
    model_speed_u = np.linspace(0,25,1000)
    model_power_u = f_up(model_speed_u)
    
    fig = plt.figure('down'+'_'+str(cap))
    ax = fig.add_subplot(111)
    ax.grid(which= 'major')
    plt.ylim(0, cap*1.1)
    plt.xlim(0, 30)
    ax.set_title('click to build down-limite line')
    ax.plot(input_data['wspd'].values,input_data['power'].values,'.')
    ax.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g') 
    ax.plot(v_line['x'].values,v_line['y'].values,linestyle='-', color='g')         
    plt.plot(model_speed_u, model_power_u, linestyle=' ', marker='.', color='r') 
    line, = ax.plot([0], [0])  
    data_limit_down = LineBuilder_down(line)
    plt.show()
        
    data_limit_down = pd.read_csv('select_down.csv')
    f_down = interpolate.interp1d(data_limit_down['speed_d'].values,data_limit_down['power_d'].values,kind='quadratic')
    model_speed_d = np.linspace(0,25,1000)
    model_power_d = f_down(model_speed_d)
        
    for j in range(len(model_power_d)):
        if model_power_d[j]<0:
            model_power_d[j]=0 
        if model_power_u[j]<0:
            model_power_u[j]=0
    model_speed_lilun = np.linspace(0,25,1000)
    model_power_lilun = (f_up(model_speed_lilun)+f_down(model_speed_lilun))/2
        
    Num=np.linspace(1,1000,1000)
    output=pd.DataFrame(dict(Num=Num,speed_u=model_speed_u,power_u=model_power_u,speed_d=model_speed_d,power_d=model_power_d))
    output.to_csv(str(wfid)+'.csv')
             
    fig=plt.figure(3)
    ax = fig.add_subplot(111)
    ax.grid(which= 'major')
    ax.set_title(str(cid)+'-'+str(cap)) 
    plt.sca(ax)
    #plt.ylim(0, cap*1.1)
    #plt.xlim(0, 25)
    plt.plot(input_data['wspd'].values,input_data['power'].values,'.')
    plt.plot(cap_line['x'].values,cap_line['y'].values,linestyle=' ', marker='.', color='g')         
    plt.plot(model_speed_u, model_power_u, linestyle='-', color='r')        
    plt.plot(model_speed_d, model_power_d, linestyle='-', color='r')
    plt.plot(model_speed_lilun, model_power_lilun, linestyle='-', color='y')
    label=['Raw','Cap']
    plt.legend(label,loc=0) 
    plt.savefig(str(cid)+'_'+'.jpg')
    plt.show()
            
    insert_filter_config(output,wfid)
    print "Finish:",wfid,sname