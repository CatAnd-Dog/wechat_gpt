import sqlite3

# 更新为数据库长连接

class SqlData(object):
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS muban_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            pageurl INTEGER,
            UNIQUE(pageurl)
        );
        '''
        create_index_query = '''CREATE INDEX IF NOT EXISTS idx_pageurl ON muban_logs(pageurl);'''
        cursor = self.connection.cursor()
        try:
            cursor.execute(create_table_query)
            cursor.execute(create_index_query)
            self.connection.commit()
        finally:
            cursor.close()  # 明确关闭游标   

    # 返回所有查询结果
    def execute_query(self, query,*args):
        cursor = self.connection.cursor()
        result = 'error'
        try:
            cursor.execute(query,*args)
            result = cursor.fetchall()
        finally:
            cursor.close()  # 明确关闭游标   
        return result
    
    # 返回单个查询结果
    def execute_query_one(self, query,*args):
        cursor = self.connection.cursor()
        result = 'error'
        try:
            cursor.execute(query,*args)
            result = cursor.fetchone()
        finally:
            cursor.close()  # 明确关闭游标 
        return result

    def execute_update(self, query,*args):
        cursor = self.connection.cursor()
        result='error'
        try:
            cursor.execute(query,*args)
            self.connection.commit()
            result='success'
        finally:
            cursor.close()  # 明确关闭游标
        return result

    # 关闭数据库连接
    def close(self):
        self.connection.close()
        



