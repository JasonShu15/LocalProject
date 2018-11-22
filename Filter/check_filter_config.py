# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 13:54:59 2018

@author: PIAO
"""

from WindFarm import WindFarm as WF
import filterpool as fp


'''
图一：原始数据
图二：排除异常数据
图三：黑色点为异常数据赋值为可用功率的点
'''

if __name__ == '__main__':
    
    #需要设置变量 start end cid
    start, end = '2018-01-01', '2018-08-23'
    cid = 'TRSSJF_652204'
    
    windfarm_info = fp.get_windfarm_info(cid)
    cap = windfarm_info['powercap'].values
    wfid = windfarm_info['wfid']
    sname = windfarm_info['sname']
    wth = 'MIX'
    stn_id = '001'
    WF = WF(cid)
    input_data = WF.get_merge_data(wth_source=wth, obs_source='exportdb', stn_id=stn_id, start_time=start, end_time=end, feature=['speed'])   

    filter_data, fl = fp.filter_config(input_data, cap[0], wfid[0])
    model_data = fp.filter_manual(input_data, cap[0], wfid[0])
    fp.show_fig(input_data, filter_data, fl, model_data, cid, cap[0])
    
   