import pymysql

conn = pymysql.connect(host='', user='',\
    password='', db='', charset='utf8' )

# SQL에 사용할 커서
cur = conn.cursor()

def Process_SQL(sql, type):
    cur.execute(sql)

    if type == "select1":
        Return_Data = cur.fetchone()[0]
        return Return_Data
    elif type == "select2":
        Return_Data = cur.fetchall()
        return Return_Data
    elif type == "commit":
        conn.commit()
    else:
        Return_Data = cur.fetchone()
        return Return_Data


