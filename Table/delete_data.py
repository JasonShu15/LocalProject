# -*- coding:utf-8 -*-
"""
@author:Haojie Shu
@time:2018/10/31
@description: 将jsonDB中所有表某一天的数据删除掉
"""
import pymysql.cursors
import time

start_time = time.time()
db_name = 'jsonDB'
connection = pymysql.connect(host='10.1.39.199',
                             user='algorithm_write',
                             password='algorithm0420',
                             db=db_name,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

tables = []

try:
    with connection.cursor() as cursor:
        sql1 = '''SHOW TABLES'''
        cursor.execute(sql1)
        table = cursor.fetchall()
        for i in range(len(table)):
            tables.append(table[i]['Tables_in_jsonDB'])

        for k in tables:
            sql2 = "SELECT * FROM `%s` where ptime >='2018-11-08 00:00:00' and ptime <='2018-11-08 23:45:00' " % k
            cursor.execute(sql2)
            D = cursor.fetchall()
            print k, D
        end_time = time.time()
        print 'time: %s' % (end_time-start_time)

finally:
    connection.commit()
    connection.close()

