from wechat import func
from wechat import news
import time
from wechat import config


wx_token=config.wx_token
defalut_model=config.default_model
default_reply=config.default_reply


# 组合功能类

class clt():
    def __init__(self):
        self.func = func.taguser()
        self.news = news.kefu()
        self.muban = news.muban()
        self.chat_msg = news.chat_msg()
        

    def send_text(self,user,msg):
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
        for start in range(0, len(reply), 500):
            # 截取从 start 到 start+500 的字符，发送
            self.news.send_text(user, reply[start:start + 500])
            time.sleep(10)

    def send_muban(self, template_id,user, urlred,content):
        self.muban.sendmuban(template_id, user, urlred, content)
        # tag=self.func.usertag(user)['tagid_list']
        # if 109 in tag:
        #     self.muban.sendmuban(template_id, user, urlred, content)
        #     return '发送成功'
        # return '无权限'

