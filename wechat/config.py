import os
from dotenv import load_dotenv
from . import loger
import requests


# 创建日志记录器，名字通常是当前文件名
logger = loger.setup_logger(__name__)

load_dotenv()

# 基础配置
wx_token=os.getenv('WX_TOKEN',"")
appid=os.getenv('APPID',"")
appsecret=os.getenv('APPSECRET',"")
chat_url=os.getenv('CHAT_URL',"")
chat_apikey=os.getenv('APIKEY',"")


# 默认模型和回复
all_model=os.getenv('ALL_MODEL',"gpt-4o-mini")
all_model_list=all_model.split(",")
default_reply=os.getenv('DEFAULT_REPLY',"正在获取回复内容，请耐心等待，请勿重复发送。")


# 数据库配置
db_host=os.getenv('DB_HOST',"")


logger.info("wx_token: %s",wx_token)
logger.info("appid: %s",appid)
logger.info("appsecret: %s",appsecret)
logger.info("chat_url: %s",chat_url)
logger.info("chat_apikey: %s",chat_apikey)
logger.info("default_model: %s",all_model_list)
logger.info("default_reply: %s",default_reply)
logger.info("db_host: %s",db_host)


def get_token():
    headers = {'Content-Type': 'application/json'}  # 明确设置请求头
    url="https://api.weixin.qq.com/cgi-bin/stable_token"
    data={
        "grant_type":"client_credential",
        "appid":appid,
        "secret":appsecret
    }
    try:
        req=requests.post(url,headers,json=data)
        token=req.json()['access_token']
        loger.info("token: %s",token)
        return token
    except Exception as e:
        logger.error("获取token失败: %s",str(e))
        return ""