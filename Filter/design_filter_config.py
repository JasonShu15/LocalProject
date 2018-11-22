# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 10:05:39 2018

@author: PIAO
"""

from WindFarm import WindFarm as WF
import filterpool as fp


if __name__ == '__main__':

    start, end = '2018-05-01', '2018-11-19'
    cid = 'XLHXF1_652244'
    
    windfarm_info = fp.get_windfarm_info(cid)
    cap = windfarm_info['powercap'].values
    wfid = windfarm_info['wfid']
    sname = windfarm_info['sname'][0]
    wth = 'MIX'
    stn_id = '001'
    WF = WF(cid)
    input_data = WF.get_merge_data(wth_source=wth, obs_source='exportdb', stn_id=stn_id, start_time=start, end_time=end,
                                   feature=['speed'])
    fp.create_table(wfid[0])
    fp.design_line(input_data, wfid[0], cap[0], cid, sname)
