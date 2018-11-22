#coding:utf-8
import pandas as pd
from Utils.connector import mysql_conn, mysql_data, mysql_test
from Utils.config import *


class WindFarm(object):
    """
    电场类
    """
    def __init__(self, cid):
        """
        内置属性
        :param cid:电场索引作为传参
        """
        conn1 = mysql_conn('atp')
        info_file = pd.read_sql("SELECT * FROM farm_available where cid = '%s'" % cid, conn1)
        conn1.close()
        self.info_file = info_file
        self.cid = cid
        self.cap = int(info_file[info_file['cid'] == str(cid)]['power_cap'].values[0])
        self.weather_code = info_file[info_file['cid'] == str(cid)]['weather_code'].values[0]
        self.manual_model = info_file[info_file['cid'] == str(cid)]['manual_model'].values[0]
        try:
            self.wf_id = info_file[info_file['cid'] == str(cid)]['ftp_dir'].values[0]
            self.previous_time = info_file[info_file['cid'] == str(cid)]['previous_time'].values[0]
            self.train_period = info_file[info_file['cid'] == str(cid)]['train_period'].values[0]
            self.obs_last_time = info_file[info_file['cid'] == str(cid)]['obs_last_time'].values[0]
            self.test_range = info_file[info_file['cid'] == str(cid)]['test_range'].values[0]
            self.preserve = info_file[info_file['cid'] == str(cid)]['preserve_box'].values[0]
            self.f_type = info_file[info_file['cid'] == str(cid)]['f_type'].values[0]
            self.ranking_accord = info_file[info_file['cid'] == str(cid)]['ranking_accord'].values[0]
            conn2 = mysql_conn('WindFarmdb')
            self.wc_info = pd.read_sql("SELECT * FROM weather_coordinates where weather_code = '%s'" % self.weather_code,
                                       conn2)
            conn2.close()
            self.wind_max = 25
            self.wind_min = 0
            self.cap_min = 0
            # ------------ 可配置项 -----------------#
            self.model_path = model_root_path + str(cid) + '/'
        except IndexError as e:
            print(e)

    def get_weather_data(self, wth_source, stn_id=None, start_time='2017-05-01', end_time='2099-12-31', feature=['speed']):
        """
        读取气象历史数据
        :param wth_source: 气象源，'CMA'、'GFS'…… 新增气象源在data_source_conf 配置
        :param stn_id:
        :param start_time: '2017-05-01'
        :param end_time: '2099-12-31'
        :param feature: 所要提取的特征，['speed', 'direction', 'airdensity']
        :return: ptime, {feature}, longitude, latitude
        """
        conn1 = mysql_data(db='nwpdb2')
        conn2 = mysql_data(db='correct_nwpdb')
        val_wth = wth_source_conf[wth_source]  # 气象源
        table_name = 'wpf_' + str(self.wf_id) + '_' + str(self.weather_code) + '_' + val_wth
        # 处理光伏
        # f = {'radiation': 'irradiance'}
        # m_feature = [f[i.split('_')[0]] if i.split('_')[0] in f.keys() else i for i in feature]

        sql = '''
            SELECT ptime,longitude,latitude,{feature}
            FROM  {table} 
            where speed<50 and ptime between '{start}' and '{end}'
            order by ptime
             '''.format(table=table_name, start=start_time, end=end_time,
                        feature=','.join(list(set([i.split('_')[0] for i in feature]))))
        if val_wth in ['CMA', 'GFS1', 'ML', 'EC']:
            data = pd.read_sql(sql, conn1)
            conn1.close()
        elif val_wth in ['MIX_correct', 'METE_correct', 'PVS_correct']:
            data = pd.read_sql(sql, conn2)
            conn2.close()
        else:
            raise IOError("%s Weather source does not exists!" % wth_source)
        if stn_id:
            lon = self.wc_info[self.wc_info['stn_id']==stn_id]['lon'].values[0]
            lat = self.wc_info[self.wc_info['stn_id']==stn_id]['lat'].values[0]
        else:
            lon = data['longitude'][0]
            lat = data['latitude'][0]
        filter_data = data[(data['longitude'] == lon) & (data['latitude'] == lat)]
        filter_data = filter_data.drop(['longitude', 'latitude'], axis=1)
        return filter_data

    def get_obs_data(self, obs_source='exportdb', start_time='2017-05-01', end_time='2099-12-31'):
        """
        提取实测数据
        :param obs_source: 实测数据源
        :param start_time: 数据起始时间
        :param end_time: 数据截止时间
        :return: DataFrame
        """
        conn1 = mysql_data('exportdb')
        conn2 = mysql_data('measuredb')
        conn3 = mysql_data('centraldb')
        val_obs = obs_source_conf[obs_source]
        table_name = val_obs + '_' + str(self.wf_id)
        data = pd.DataFrame()

        if obs_source == 'exportdb':#提取数据已做更改
            sql = '''
                SELECT rectime,predict_wspd,wspd,predict_power,theorypower,power
                FROM  {table} 
                where rectime between '{start}' and '{end}'
                and power >= 0 
                order by rectime  
                '''.format(table=table_name, start=start_time, end=end_time)
            data = pd.read_sql(sql, conn1)

        elif obs_source == 'measuredb':
            sql = '''
                SELECT rectime,wspd,power
                FROM  {table} 
                where rectime between '{start}' and '{end}'
                order by rectime  
                '''.format(table=table_name, start=start_time, end=end_time)
            data = pd.read_sql(sql, conn2)

        elif obs_source == 'centraldb':   # 单风机数据整理为多label
            sql = '''
                SELECT rectime,wtid,wspd,power,theorypower
                FROM  {table} 
                where rectime between '{start}' and '{end}'
                order by rectime            
                '''.format(table=table_name, start=start_time, end=end_time)
            df = pd.read_sql(sql, conn3).dropna()
            df['limit'] = df['power'] / df['theorypower']
            df.loc[df['limit'] > 1, 'limit'] = 1
            df.loc[df['limit'] < 0, 'limit'] = 1
            wtid = df['wtid'].drop_duplicates().reset_index(drop=True)
            data_temp = df.loc[df['wtid'] == wtid[0], ['rectime', 'power', 'theorypower', 'limit']]
            for i in range(1, len(wtid)):
                temp = df.loc[df['wtid'] == wtid[i], ['rectime', 'power', 'theorypower', 'limit']]
                data_temp = pd.merge(data_temp, temp, on='rectime', how='inner',
                                     suffixes=('_%s' % wtid[i-1], '_%s' % wtid[i]))
            # 重命名最后一个风机编号数据
            last = wtid.iloc[-1]
            data = data_temp.rename(columns={"power": "power_%s" % last, "theorypower": "theorypower_%s" % last,
                                             "limit": "limit_%s" % last})

        data.rename(columns={"rectime": "ptime"}, inplace=True)
        conn1.close()
        conn2.close()
        conn3.close()
        return data

    def get_merge_data(self, wth_source='CMA', obs_source='exportdb', stn_id='001', start_time='2017-05-01',
                       end_time='2099-12-31', feature=['speed']):
        """
        返回气象数据、实测数据合并的结果
        :param wth_source: 气象源
        :param obs_source: 实测源
        :param stn_id:
        :param start_time: 数据起始时间
        :param end_time: 数据截止时间
        :param feature: 参与训练的字段，默认仅风速
        :return:
        """
        if self.f_type == 'W' or self.f_type == 'WO':
            obs_data = self.get_obs_data(obs_source, start_time=start_time, end_time=end_time)
        elif self.f_type == 'S':
            obs_data = self.get_pv_data(obs_source, start_time=start_time, end_time=end_time)
        else:
            raise Exception

        if len(wth_source.split(',')) > 1:
            multi_data = self.get_multi_weather_data(wth_source, stn_id, start_time, end_time, feature)
            merge_data = pd.merge(multi_data, obs_data, how='inner', on='ptime')
        elif feature[0] == 'wspd':
            merge_data = obs_data
        else:
            weather_data = self.get_weather_data(wth_source, stn_id, start_time, end_time, feature)
            merge_data = pd.merge(weather_data, obs_data, how='inner', on='ptime')

        return merge_data

    def get_multi_weather_data(self, wth_source, stn_id, start_time='2017-05-01', end_time='2099-12-31', feature=['speed']):
        """
        提取多气象源数据
        :param wth_source = 'CMA, GFS'
        :param stn_id
        :param start_time: 数据起始时间
        :param end_time: 数据截止时间
        :param feature: 参与训练的字段，默认仅风速
        :return: DateFrame
        """

        source = wth_source.strip().split(',')
        wth_data = pd.DataFrame(pd.date_range(start_time, end_time, freq='15min'), columns=['ptime'])
        for s in source:
            try:
                one = self.get_weather_data(s, stn_id, start_time, end_time, feature)
                one.columns = [one.columns[0]] + [x + '_%s' % s for x in one.columns[1:]]
                wth_data = pd.merge(wth_data, one, on='ptime', how='left')
            except:
                pass
        return wth_data

    def get_pv_data(self, obs_source='exportdb', start_time='2017-05-01', end_time='2099-12-31'):
        conn1 = mysql_data('exportdb')
        val_obs = obs_source_conf[obs_source]
        table_name = val_obs + '_' + str(self.wf_id)
        data = pd.DataFrame()
        if obs_source == 'exportdb':
            sql = '''
                SELECT rectime,predict_radiation,radiation,power,theorypower
                FROM  {table} 
                where rectime between '{start}' and '{end}'
                order by rectime  
                '''.format(table=table_name, start=start_time, end=end_time)
            data = pd.read_sql(sql, conn1)
        data.rename(columns={"rectime": "ptime"}, inplace=True)
        conn1.close()
        return data

