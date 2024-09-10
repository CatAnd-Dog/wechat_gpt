import requests
import json
from wechat.config import get_token
from wechat import config
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

# 创建一个日志器
logger = logging.getLogger(__name__)


class kefu:
    def send_text(self, user, content,agentid):
        token=get_token()
        url = config.base_url+config.url_join['message_send'].format(token)
        headers = {"Content-Type": "application/json; charset=utf-8", "Connection": "keep-alive"}
        data = {
                "touser" : user,
                "msgtype" : "text",
                "agentid" : agentid,
                "text" : {
                    "content" : content
                },
                }
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        res = requests.post(url=url, data=data, headers=headers)
        return res.json()
    
class  muban:

    def sendmuban(self, template_id,user, urlred,content):
        token=get_token()
        url = config.base_url+config.url_join['message_send'].format(token)
        headers = {"Content-Type": "application/json; charset=utf-8", "Connection": "keep-alive"}
        data = {
            "touser": user,
            "template_id": template_id,
            'url':urlred,
            "data":content
                }
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        res = requests.post(url=url, data=data, headers=headers)
        return res.json()


class chat_msg:

    def __init__(self) :
        self.chat_url=config.chat_url
        self.chat_apikey=config.chat_apikey

    def chat_gpt(self,msg,model):
        url=self.chat_url
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Sec-Fetch-Mode': 'cors',
            'Authorization': 'Bearer '+self.chat_apikey,
        }
        data={
            'model':model,
            'messages':[
                {"role": "user", "content": msg},
            ],
            'max_tokens': 2000,
          'stream': False,
        }
        req=requests.post(url,headers=headers,json=data,timeout=120)
        try:
            rep=req.json()['choices'][0]['message']['content']
        except Exception as e:
            print(e)
            logger.debug(f'''gpt请求失败，返回内容：{e}''')
            rep='gpt请求失败'
        return rep



