#coding:utf-8
import MySQLdb


def mysql_conn(db='xmlpub'):
    user = 'algorithm_group'
    pwd= 'algorithm'
    ip = '10.1.39.199'
    port = 3306
    conn_modeling = MySQLdb.connect(host=ip, db=db, user=user, passwd=pwd ,port=port, charset="utf8")
    return conn_modeling


def mysql_data(db='nwpdb2', inner=True):
    user = 'algorithm_group'
    pwd= 'algorithm'
    if inner:
        ip = '10.1.39.199'
        port = 3306
    else:
        ip = '61.49.28.225'
        port = 1000
    conn_modeling = MySQLdb.connect(host=ip, db=db, user=user, passwd=pwd ,port=port, charset="utf8")
    return conn_modeling


def mysql_test(db='central'):
    user = 'algorithm_group'
    pwd= 'algorithm'
    ip = '52.83.220.27'
    port = 3306
    conn_modeling = MySQLdb.connect(host=ip, db=db, user=user, passwd=pwd ,port=port, charset="utf8")
    return conn_modeling