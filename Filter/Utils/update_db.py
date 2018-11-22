#coding:utf-8
from Utils.connector import mysql_conn


def update_wind_farm_available(cid, db='atp', **kwargs):
    '''
    更新model_info表
    :param db:
    :param model_id:
    :param kwargs: {"runing_model":"SVM_LYLST1_654302_T01",
                    "previous_time":"2017-08-16",
                    "update_time":"2017-08-16"}
    :return:
    '''
    conn = mysql_conn(db)
    cur = conn.cursor()

    for key in kwargs:
        try:
            update_str = "update wind_farm_available set {key} = '{values}' where cid = '{cid}'"\
                .format(key=key, values=kwargs[key], cid=cid)
            cur.execute(update_str)
            conn.commit()
            print("updated wind_farm_available %s -> %s!"%(cid,key))
        except Exception as e:
            conn.rollback()
            print(e, "update wind_farm_available %s -> %s failed!"% (cid, key))
    conn.close()


def update_model_info(model_id, db='atp', **kwargs):
    '''
    更新model_info表
    :param db:
    :param model_id:
    :param kwargs: {"model_id":"SVM_LYLST1_654302_T01",
                    "cid":"LYLST1_654302",
                    "mete_source":"GFS",
                    "obs_source":"exportdb",
                    "state":"1",
                    "algo_param":"{'max_depth':7,'n_estimators':35, 'learning_rate': 0.05}",
                    "score":"80",
                    "create_time":"2017-08-16",
                    "data_length":"7",
                    "update_time":"2017-08-16"}
    :return:
    '''
    conn = mysql_conn(db)
    cur = conn.cursor()

    for key in kwargs:
        try:
            update_str = "update region_model_info set {key} = '{values}' where model_id = '{mid}'"\
                .format(key=key, values=kwargs[key], mid=model_id)
            cur.execute(update_str)
            conn.commit()
            print("updated model_info %s -> %s!" % (model_id, key))
        except Exception as e:
            conn.rollback()
            print(e, "update model_info %s -> %s failed!"% (model_id, key))
    conn.close()


def update_report_record(db='atp', **kwargs):
    '''
    更新report_record表
    :param db:
    :param model_id:
    :param kwargs: {"method_id":"LYLST1_654302_M01",
                    "cid":"LYLST1_654302",
                    "datetime":"2017-08-16"}
    :return:
    '''
    conn = mysql_conn(db)
    cur = conn.cursor()
    try:
        k = ",".join(kwargs.keys())
        v = ",".join(map(lambda x: "\'%s\'" % x.encode('utf8'), kwargs.values()))
        update_str = "insert into report_record({key}) values({values})"\
            .format(key=k, values=v)
        cur.execute(update_str)
        conn.commit()
        print("%s insert into record!" % kwargs['method_id'])
    except Exception as e:
        conn.rollback()
        print(e)
    conn.close()



def update_train_log(db='atp', **kwargs):
    '''
    更新train_log表
    :param db:
    :param model_id:
    :param kwargs: {"model_id":"SVM_LYLST1_654302_T01",
                    "cid":"LYLST1_654302",
                    "log_time":"2017-08-16",
                    "state":"1",
                    "logging":"#$%^#$"}
    :return:
    '''
    conn = mysql_conn(db)
    cur = conn.cursor()
    try:
        k = ",".join(kwargs.keys())
        v = ",".join(map(lambda x: "\'%s\'" % x.encode('utf8'), kwargs.values()))
        update_str = "insert into train_log({key}) values({values})"\
            .format(key=k, values=v)
        cur.execute(update_str)
        conn.commit()
        print(kwargs['logging'])
    except Exception as e:
        conn.rollback()
        print(e)
    conn.close()


def update_forecast_log(db='atp', **kwargs):
    '''
    更新forecast_log表
    :param db:
    :param kwargs: {"cid":"LYLST1_654302",
                    "method_id":"LYLST1_654302_M01",
                    "log_time":"2017-08-16",
                    "state":"1",
                    "logging":"#$%^#$"}
    :return:
    '''
    conn = mysql_conn(db)
    cur = conn.cursor()
    try:
        k = ",".join(kwargs.keys())
        v = ",".join(map(lambda x: "\'%s\'" % x.encode('utf8'), kwargs.values()))
        update_str = "insert into forecast_log({key}) values({values})".format(key=k, values=v)
        cur.execute(update_str)
        conn.commit()
        print(kwargs['logging'])
    except Exception as e:
        conn.rollback()
        print(e)
    conn.close()
