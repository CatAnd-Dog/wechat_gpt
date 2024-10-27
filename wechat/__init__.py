
from . import func
from . import news
import time
from . import config
from . import sqldata
from . import loger
import time
from cachetools import TTLCache, cached
from cachetools.keys import hashkey

# 默认模型
all_model=config.all_model_list

logger = loger.setup_logger(__name__)

db_host=config.db_host


# 创建一个TTLCache用于存储access_token，容量为1，过期时间为6000秒
access_token_cache = TTLCache(maxsize=1, ttl=6000)

@cached(access_token_cache, key=lambda _: hashkey("access_token"))
def get_access_token():
    """
    获取access_token，如果缓存过期则自动刷新。
    """
    return config.get_token()


# 创建一个TTLCache用于存储userid到content列表的映射，容量为1000，过期时间为600秒（10分钟）
id_content_cache = TTLCache(maxsize=1000, ttl=600)

def add_content_to_id(id_, content):
    """
    添加content到指定id的列表中。
    如果id不存在，则创建新的列表。
    """
    with id_content_cache.lock:
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
    with id_content_cache.lock:
        return list(id_content_cache.get(id_, []))


# 组合功能类
class clt():
    def __init__(self):
        # 标签功能---用于权限控制
        self.func = func.taguser()
        # 客服功能--发送客服消息
        self.news = news.kefu()
        # 模板消息功能
        self.muban = news.muban()
        # 聊天功能---调用gpt模型
        self.chat_msg = news.chat_msg()
    
    # 发送文本消息
    def send_text(self,user,msg):
        token = get_access_token()
        # 发送正在输入状态
        self.news.kefu_status(user,'Typing',token)
        parts  = msg[:10].split(' ', 1)
        logger.debug("用户消息: %s",parts)
        if parts[0] in all_model:  # 如果消息以模型名称开头,则使用该模型回复
            message= {'role': 'user', 'content': parts[1]}
            model=parts[0]
        else: # 否则使用默认模型回复，默认模型为 all_model[0]
            message = {'role': 'user', 'content': msg}
            model=all_model[0]
        # 构造消息
        add_content_to_id(user, message)
        # 获取构造后的消息,最多7条
        contents = get_contents_by_id(user)[-7:]
        # 调用模型回复
        reply=self.chat_msg.chat_gpt(contents,model)
        # 构造回复消息,为了避免回复过长，只取前500字符
        reply_message = {"role": "assistant", "content": reply[:500]}
        add_content_to_id(user, reply_message)
        # 如果回复长度超过 500 字符，分批发送
        for start in range(0, len(reply), 500):
            # 截取从 start 到 start+500 的字符，发送
            self.news.send_text(user, reply[start:start + 500],token)
            time.sleep(5)
        # 发送完成
        self.news.kefu_status(user,'CancelTyping',token)

    # 清除用户记忆消息
    def clean_usermsg(self,user):
        id_content_cache.pop(user, None)

    # 发送模板消息
    def send_muban(self, template_id,user, urlred,content):
        token = get_access_token()
        self.muban.sendmuban(template_id, user, urlred, content,token)
        logger.debug("template_id: %s, user: %s, urlred: %s, content: %s",template_id, user, urlred, content)
        return 'success'


# 数据库操作类
class dbdata_clt():
    def __init__(self) :
        if db_host :
            self.place_holder = 's%'
            self.db=''
        else:
            # 修改占位符
            self.place_holder = '?'
            # 初始化数据库连接配置
            self.db=sqldata.SqlData('./data/wechat.db')

    def get_data(self,*args):
        sql= f'''SELECT * FROM muban_logs WHERE pageurl = {self.place_holder} '''
        return self.db.execute_query_one(sql,*args)
    
    def insert_data(self,*args):
        sql= f'''INSERT INTO muban_logs (content, pageurl) VALUES ({self.place_holder},{self.place_holder})'''
        return self.db.execute_update(sql,*args)
        