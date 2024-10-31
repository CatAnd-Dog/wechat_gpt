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
adminid=os.getenv('ADMIN_ID',"")

# 数据库配置
db_host=os.getenv('DB_HOST',"")
notify_url=os.getenv('NOTIFY_URL',"")


# 读取confif.json文件
with open('config.json', 'r') as f:
    config_else = json.load(f)

# 标签权限
Tags=config_else['Tags']
# 聊天控制
ChatMsg=config_else['ChatMsg']


logger.info("wx_token: %s",wx_token)
logger.info("appid: %s",appid)
logger.info("appsecret: %s",appsecret)
logger.info("chat_url: %s",chat_url)
logger.info("chat_apikey: %s",chat_apikey)
logger.info("default_model: %s",default_model)
logger.info("default_reply: %s",default_reply)
logger.info("db_host: %s",adminid)
logger.info("admin: %s",db_host)
logger.info("权限标签: %s",Tags)
logger.info("聊天控制: %s",ChatMsg)
logger.info("notify_url: %s",notify_url)


def get_token():
    url="https://api.weixin.qq.com/cgi-bin/stable_token"
    data={
        "grant_type":"client_credential",
        "appid":appid,
        "secret":appsecret
    }
    req=requests.post(url,json=data)
    try:
        token=req.json()['access_token']
        logger.info("token: %s",token)
        return token
    except Exception as e:
        logger.error("token返回信息: %s",req.text)
        logger.error("获取token失败: %s",str(e))
        return ""
    

# 添加错误验证提示
def display_error(req):
    if 'errcode' not in req or req['errcode']==0:
        return req
    else:
        logger.error("发生严重错误：{}".format(req))
        return req