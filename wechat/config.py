import os
from dotenv import load_dotenv


load_dotenv()

# 基础配置
wx_token=os.getenv('WX_TOKEN',"")
appid=os.getenv('APPID',"")
appsecret=os.getenv('APPSECRET',"")
chat_url=os.getenv('CHAT_URL',"")
chat_apikey=os.getenv('APIKEY',"")

# 默认模型和回复
default_model=os.getenv('DEFAULT_MODEL',"gpt-3.5-turbo")
default_reply=os.getenv('DEFAULT_REPLY',"正在获取回复内容，请耐心等待，请勿重复发送。")



# 数据库配置
db_host=os.getenv('DB_HOST',"")


headers = {'Content-Type': 'application/json'}  # 明确设置请求头

import requests

import time
token=""


# org_time=int(time.time())
org_time=0

def get_token():
    global token,org_time
    nowtime=int(time.time())
    if nowtime - org_time > 200:
        url="https://api.weixin.qq.com/cgi-bin/stable_token"
        data={
            "grant_type":"client_credential",
            "appid":appid,
            "secret":appsecret
        }
        req=requests.post(url,json=data)
        token=req.json()['access_token']
        org_time=nowtime
        print('token updated')
        return token
    print('token not updated')
    return token

# print(get_token())
# print(org_time)
