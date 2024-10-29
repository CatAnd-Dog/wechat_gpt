import os
from dotenv import load_dotenv
from . import loger
import requests
import json

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
default_model=os.getenv('DEF_MODEL',"gpt-4o-mini")
default_reply=os.getenv('DEFAULT_REPLY',"正在获取回复内容，请耐心等待，请勿重复发送。")


# 数据库配置
db_host=os.getenv('DB_HOST',"")



# 读取confif.json文件
with open('config.json', 'r') as f:
    config_else = json.load(f)


Tags=config_else['Tags']

logger.info("wx_token: %s",wx_token)
logger.info("appid: %s",appid)
logger.info("appsecret: %s",appsecret)
logger.info("chat_url: %s",chat_url)
logger.info("chat_apikey: %s",chat_apikey)
logger.info("default_model: %s",default_model)
logger.info("default_reply: %s",default_reply)
logger.info("db_host: %s",db_host)
logger.info("权限标签: %s",Tags)


def get_token():
    url="https://api.weixin.qq.com/cgi-bin/stable_token"
    data={
        "grant_type":"client_credential",
        "appid":appid,
        "secret":appsecret
    }
    try:
        req=requests.post(url,json=data)
        token=req.json()['access_token']
        logger.info("token: %s",token)
        return token
    except Exception as e:
        logger.error("获取token失败: %s",str(e))
        return ""