import os
from dotenv import load_dotenv


load_dotenv()

wx_token=os.getenv('WX_TOKEN',"")
appid=os.getenv('APPID',"")
appsecret=os.getenv('APPSECRET',"")
chat_url=os.getenv('CHAT_URL',"")
chat_apikey=os.getenv('APIKEY',"")



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
