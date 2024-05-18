import wechat
print(wechat.db_host)
clt=wechat.dbdata_clt()
a=clt.get_data([8888])
print(a[1])
# import sqlite3

# db='./data/wechat.db'
# connection = sqlite3.connect(db)
# cursor = connection.cursor()
# print('Opened database successfully')
# cursor.close()
# connection.close()
