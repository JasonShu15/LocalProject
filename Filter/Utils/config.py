#coding:utf-8
import os

"""
系统路径配置
"""
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR_LIST = BASE_DIR.split('/')
# BASE_DIR = '/'.join(BASE_DIR_LIST[:-2])+'/'
BASE_DIR = '/opt/atp_data/'
mnt_dir = '/mnt/pub/json_files/'

log_root_path = mnt_dir+'logs/'
json_path = mnt_dir+'forecast_result/json/'
xml_path = mnt_dir+'forecast_result/xml/'
model_root_path = mnt_dir+'models/'
# 缓存
forecast_cache = BASE_DIR+'cache/'

# 气象文件地址
CMA_path = '/mnt/pub/cma9km_new_op/'
GFS_path = '/mnt/pub/wrf_new_op/'
EC_GFS_path = '/mnt/pub/ec_gfs_merge/'
EC_path = '/mnt/pub/ecmwf_new_op/'
MIX_path = '/mnt/pub/correct_new_op/Mix_data/'
PVS_path = '/mnt/pub/correct_new_op/Correct_Pvs_data/'
METE_path = '/mnt/pub/correct_new_op/Correct_data/'
METEpv_path = '/mnt/pub/correct_new_op/Correct_Pvs_data/'
custom_wth_path = '/mnt/pub/correct_new_op/Mix_Mete_data/'
Monthly_path = '/mnt/pub/cfs_monthly_extract/'
ML_path = '/mnt/pub/extract_data_third_party/meteologica/'

# 海洋
sea_file_path = '/mnt/pub/extract_sea_op/'

# 上报文件生成位置
report_path = '/mnt/pub/extract_data_third_party/zuoliye/WPF/'
monthly_json_path = '/mnt/pub/json_files/forecast_result/monthly/'

# 气象源名称与历史气象表后缀对应关系
wth_source_conf = {
            'CMA': 'CMA',
            'GFS': 'GFS1',
            'ECGFS': 'EC',
            'ML': 'ML',
            'MIX': 'MIX_correct',
            'METE': 'METE_correct',
            'MM': 'MIX_correct',
            'EC': 'EC',
            'PVS': 'PVS_correct'
}

# 实测源名称与历史实测表后缀对应关系
obs_source_conf = {
    'exportdb': 'factory',
    'measuredb': 'wf',
    'centraldb': 'wf'
}

# 气象历史与气象预报数据字段对应关系
feature_list = {
            'speed': 'wspd',
            'wspd':'wspd',
            'temperature': 't',
            'direction': 'wdir',
            'rhumidity': 'rh',
            'pressure': 'p',
            'airdensity': 'rhoair',
            'irradiance': 'ghi'
        }

# 默认训练窗口
windows_default = 15

# 各气象源的文件时间
fst_wth_clock = {
    'CMA': ['12'],
    'ECGFS': ['00', '12'],
    'MIX': ['00', '12'],
    'MM': ['12'],
    'EC': ['00', '12'],
    'METE': ['12'],
    'GFS': ['00', '12'],
    'MUL': ['12'],
    'ML': ['06'],
    'PVS':['12']
}

# 限电起始风速
start_limit_wind_speed = 6
