from wechat import func
from wechat import news
import time
from wechat import config
from wechat import sqldata


wx_token=config.wx_token
appid=config.appid
EncodingAESKey=config.EncodingAESKey
defalut_model=config.default_model
default_reply=config.default_reply

db_host=config.db_host


# 组合功能类

class clt():
    def __init__(self):
        self.func = func.taguser()
        self.news = news.kefu()
        self.muban = news.muban()
        self.chat_msg = news.chat_msg()
        

    def send_text(self,user,msg,agentid):
        # tag=self.func.usertag(user)['tagid_list']  # 权限控制部分
        reply="你好，请联系作者"
        if msg.startswith('gpt'):
            parts  = msg.split(' ', 1)
            reply=self.chat_msg.chat_gpt(parts[1],parts[0])
        else:
            reply=self.chat_msg.chat_gpt(msg,defalut_model)
        # msg以gpt开头
        # if 100 in tag and msg.startswith('gpt4'):
        #     reply=self.getreply(msg,'chat-gpt-4')
        # elif 101 in tag and msg.startswith('gpt3'):
        #     reply=self.getreply(msg,'gpt-3.5-turbo-1106')
        
        # 如果回复长度超过 500 字符，分批发送
        for start in range(0, len(reply), 1500):
            # 截取从 start 到 start+500 的字符，发送
            self.news.send_text(user, reply[start:start + 1500],agentid)
            time.sleep(10)

    def send_muban(self, template_id,user, urlred,content):
        self.muban.sendmuban(template_id, user, urlred, content)
        # tag=self.func.usertag(user)['tagid_list']
        # if 109 in tag:
        #     self.muban.sendmuban(template_id, user, urlred, content)
        #     return '发送成功'
        # return '无权限'

class dbdata_clt():
    def __init__(self) :
        if db_host :
            self.place_holder = 's%'
            self.db=''
        else:
            # 修改占位符
            self.place_holder = '?'
            # 初始化数据库连接配置
            self.db=sqldata.SqlData('./data/wechat.db')

    def get_data(self,*args):
        sql= f'''SELECT * FROM muban_logs WHERE pageurl = {self.place_holder} '''
        return self.db.execute_query_one(sql,*args)
    
    def insert_data(self,*args):
        sql= f'''INSERT INTO muban_logs (content, pageurl) VALUES ({self.place_holder},{self.place_holder})'''
        return self.db.execute_update(sql,*args)
        