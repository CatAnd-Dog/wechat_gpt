from . import news
import time
from . import config
from . import loger
import time
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from threading import Lock

# 默认模型
all_model=config.all_model_list
appid=config.appid
appsecret=config.appsecret

logger = loger.setup_logger(__name__)

# 创建一个TTLCache用于存储access_token，容量为1，过期时间为6000秒
access_token_cache = TTLCache(maxsize=1, ttl=6000)

@cached(access_token_cache, key=lambda *args, **kwargs: hashkey("access_token"))
def get_access_token():
    """
    获取access_token，如果缓存过期则自动刷新。
    """
    return config.get_token()


# 创建一个TTLCache用于存储userid到content列表的映射，容量为1000，过期时间为600秒（10分钟）
id_content_cache = TTLCache(maxsize=1000, ttl=600)
cache_lock = Lock()
def add_content_to_id(id_, content):
    """
    添加content到指定id的列表中。
    如果id不存在，则创建新的列表。
    """
    with cache_lock:
        if id_ in id_content_cache:
            id_content_cache[id_].append(content)
        else:
            id_content_cache[id_] = [content]
        # 访问或更新id会刷新其过期时间
        return list(id_content_cache[id_])

def get_contents_by_id(id_):
    """
    获取指定id的内容列表。
    如果id不存在，则返回空列表。
    """
    with cache_lock:
        return list(id_content_cache.get(id_, []))


# 组合功能类
class clt():
    def __init__(self):
        # 客服功能--发送客服消息
        self.news = news.kefu()
        # 聊天功能---调用gpt模型
        self.chat_msg = news.chat_msg()

    # 处理用户消息
    def deal_msg(self, user, msg):
        
        parts  = msg.split(' ', 1)
        if parts[0] in all_model:  # 如果消息以模型名称开头,则使用该模型回复
            message= {'role': 'user', 'content': parts[1]}
            model=parts[0]
        else: # 否则使用默认模型回复，默认模型为 all_model[0]
            message = {'role': 'user', 'content': msg}
            model=all_model[0]
        # 构造消息
        add_content_to_id(user, message)
        # 获取构造后的消息,最多7条
        contents = get_contents_by_id(user)[(-1) * config.max_num:]
        logger.debug("用户消息数组: %s",contents)
        return contents,model
    
    # 处理回复消息
    def deal_msg2(self, user, msg):
        # 构造回复消息,为了避免回复过长，只取前500字符
        reply_message = {"role": "assistant", "content": msg}
        add_content_to_id(user, reply_message)
 

    # 发送文本消息
    def send_text(self,user,msg,model):
        token = get_access_token()
        # 发送正在输入状态
        self.news.kefu_status(user,'Typing',token)
        # 调用模型回复
        reply=self.chat_msg.chat_gpt(msg,model)
        # 打印回复
        logger.debug("gpt回复内容: %s",reply)
        # 如果回复长度超过 500 字符，分批发送
        for start in range(0, len(reply), 500):
            # 截取从 start 到 start+500 的字符，发送
            self.news.send_text(user, reply[start:start + 500],token)
            time.sleep(1)
        # 发送完成
        self.deal_msg2(user,reply[:500])
        self.news.kefu_status(user,'CancelTyping',token)

    # 清除用户记忆消息
    def clean_usermsg(self,user):
        id_content_cache.pop(user, None)
