import sqlite3


class SqlData(object):
    def __init__(self, db_path):
        self.db_path=db_path
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS muban_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            pageurl INTEGER,
            UNIQUE(pageurl)
        );
        CREATE INDEX IF NOT EXISTS idx_pageurl ON muban_logs(pageurl);
        '''
        try:
            self.connect()
            self.cursor.executescript(create_table_query)
            self.connection.commit()
        finally:
            self.close()

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        

    # 返回所有查询结果
    def execute_query(self, query,*args):
        result = ''
        try:
            self.connect()
            self.cursor.execute(query,*args)
            result = self.cursor.fetchall()
        finally:
            self.close()
        return result
    
    # 返回单个查询结果
    def execute_query_one(self, query,*args):
        result = ''
        try:
            self.connect()
            self.cursor.execute(query,*args)
            result = self.cursor.fetchone()
        finally:
            self.close()
        return result

    def execute_update(self, query,*args):
        result='error'
        try:
            self.connect()
            self.cursor.execute(query,*args)
            self.connection.commit()
            result='success'
        finally:
            self.close()
        return result

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except:
            self.connection.close()
        



