import requests
import json
from config import get_token
import config

class kefu:
    def send_text(self, user, content):
        token=get_token()
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={}".format(token)
        headers = {"Content-Type": "application/json; charset=utf-8", "Connection": "keep-alive"}
        data = {
            "touser": user,
            "msgtype": "text",
            "text":{ "content": content}
                }
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        res = requests.post(url=url, data=data, headers=headers)
        return res.json()
    
class  muban:

    def sendmuban(self, template_id,user, urlred,content):
        token=get_token()
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(token)
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
        }
        req=requests.post(url,headers=headers,json=data,timeout=120)
        try:
            rep=req.json()['choices'][0]['message']['content']
        except Exception as e:
            print(e)
            rep='gpt请求失败'
        return rep




