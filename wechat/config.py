import os
from dotenv import load_dotenv


load_dotenv()

# 基础配置
wx_token=os.getenv('WX_TOKEN',"")
appid=os.getenv('APPID',"")
EncodingAESKey=os.getenv('EncodingAESKey',"")
appsecret=os.getenv('APPSECRET',"")
chat_url=os.getenv('CHAT_URL',"")
chat_apikey=os.getenv('APIKEY',"")
base_url=os.getenv('BASE_URL',"https://qyapi.weixin.qq.com/cgi-bin")

# 默认模型和回复
default_model=os.getenv('DEFAULT_MODEL',"gpt-3.5-turbo")
default_reply=os.getenv('DEFAULT_REPLY',"正在获取回复内容，请耐心等待，请勿重复发送。")


# 数据库配置
db_host=os.getenv('DB_HOST',"")


# url
url_join={
'gettoken':'/gettoken?corpid={}&corpsecret={}',
'message_send':'/message/send?access_token={}',

}





# 以下是获取access_token的代码

import requests
import time
token=""

org_time=int(time.time())
org_time=0
def get_token(secret=appsecret):
    global token,org_time
    nowtime=int(time.time())
    if nowtime - org_time > 200:
        url=base_url+url_join['gettoken'].format(appid,secret)
        req=requests.get(url)
        token=req.json()['access_token']
        expirestime=req.json()['expires_in']
        org_time=nowtime
        print(expirestime)
        print('token updated')
        return token
    print('token not updated')
    return token

