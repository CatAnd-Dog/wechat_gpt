
from . import func
from . import news
import time
from . import config
from . import sqldata
from . import loger
import time
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from threading import Lock

# 默认模型
default_model=config.default_model
appid=config.appid
appsecret=config.appsecret

logger = loger.setup_logger(__name__)

db_host=config.db_host


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
            id_content_cache[id_] += content
        else:
            id_content_cache[id_] = content
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
        # 标签功能---用于权限控制
        self.func = func.taguser()
        # 客服功能--发送客服消息
        self.news = news.kefu()
        # 模板消息功能
        self.muban = news.muban()
        # 聊天功能---调用gpt模型
        self.chat_msg = news.chat_msg()
        # 初始化标签---用于权限控制
        self.auth_list = self.init_tag()
 
    # 初始化标签
    def init_tag(self):
        token = get_access_token()
        auth_list={}
        # 获取标签列表
        taglist = self.func.gettag(token)['tags']
        taglist_dic= {tag['name']: tag['id'] for tag in taglist}
        for tag in config.Tags:
            # 如果标签不存在则创建
            if tag not in taglist_dic:
                req=self.func.creattag(tag, token)
                auth_list[req['tag']['id']]=config.Tags.get(tag)
            else:
                auth_list[taglist_dic.get(tag)]=config.Tags.get(tag)
        return auth_list
   

    # 把用户消息存入缓存
    def deal_msg(self, user, msg):
        logger.debug("用户消息: %s",msg)
        parts  = msg.split(' ', 1)
        if parts[0] in []:  # 如果消息以模型名称开头,则使用该模型回复
            message= {'role': 'user', 'content': parts[1]}
            model=parts[0]
        else: # 否则使用默认模型回复，默认模型为 all_model[0]
            message = {'role': 'user', 'content': msg}
            model=default_model
        # 构造消息
        add_content_to_id(user, [message])
        contents = get_contents_by_id(user)[-7:]
        return contents,model
    
    # 把回复消息存入缓存
    def deal_msg2(self, user, msg):
        add_content_to_id(user, msg)
 
    # 发送文本消息
    def send_text(self,user,msg,model):
        token = get_access_token()
        # 发送正在输入状态
        self.news.kefu_status(user,'Typing',token)
        usertag = self.func.usertag(user,token)['tagid_list']
        # 查询用户权限
        auth = [self.auth_list.get(tag) for tag in usertag]
        auth= sum(auth, [])
        # 判断用户权限
        if model not in auth:
            reply = "您没有权限使用该模型，请联系管理员。"
        else:
            # 调用模型回复
            # 判断是否需要总结
            logger.debug("用户消息数组: %s",msg)
            # if len(msg) > 8:
            #     prompt = {'role': 'user', 'content': '请概述我们之前的所有对话内容，以此作为我们接下来对话的提示.'}
            #     # 把用户消息先提出来
            #     logger.debug("用户消息: %s",msg)
            #     user_msg = msg[-1]
            #     # 替换为总结提示
            #     msg[-1] = prompt
            #     reply_s = self.summary(msg)
            #     # 获取总结回复
            #     reply_message = {"role": "system", "content": reply_s}
            #     self.clean_usermsg(user)
            #     # 构造用户消息
            #     msg = [reply_message, user_msg]
            #     # 把用户消息存入缓存
            #     self.deal_msg2(user,msg)
            
            reply=self.chat_msg.chat_gpt(msg,model)
        
        # 如果回复长度超过 500 字符，分批发送
        for start in range(0, len(reply), 500):
            # 截取从 start 到 start+500 的字符，发送
            self.news.send_text(user, reply[start:start + 500],token)
            time.sleep(5)
        # 发送完成
        rep={"role": "assistant", "content": reply[:500]}
        # 把回复消息存入缓存
        self.deal_msg2(user,[rep])
        self.news.kefu_status(user,'CancelTyping',token)

    # 清除用户记忆消息
    def clean_usermsg(self,user):
        id_content_cache.pop(user, None)

    # 总结聊天记录，防止消息过多
    def summary(self,prompt):
        reply=self.chat_msg.chat_gpt(prompt,default_model)
        return reply

    # 发送模板消息
    def send_muban(self, template_id,user, urlred,content):
        token = get_access_token()
        usertag = self.func.usertag(user,token)['tagid_list']
        # 查询用户权限
        auth = [self.auth_list.get(tag) for tag in usertag]
        auth= sum(auth, [])
        if 'muban' not in auth:
            return 'erro'
        self.muban.sendmuban(template_id, user, urlred, content,token)
        logger.debug("template_id: %s, user: %s, urlred: %s, content: %s",template_id, user, urlred, content)
        return 'success'

    # 管理员认证---调用这个函数判断用户是否为管理员
    def is_admin(self,user):
        token = get_access_token()
        usertag = self.func.usertag(user,token)['tagid_list']
        # 查询用户权限
        auth = [self.auth_list.get(tag) for tag in usertag]
        auth= sum(auth, [])
        if 'admin' in auth:
            return True
        else:
            return False

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
        
