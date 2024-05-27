import requests
import json
from wechat.config import get_token

# 这个是管理用户标签，用来限制用户可以使用的功能
headers = {'Content-Type': 'application/json'}  # 明确设置请求头

class taguser:

    def edittag(self,id,name):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/tags/update?access_token={}".format(token)
        data={   "tag" : {    "id" : id,     "name" : name  } } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        return req.json()
    
    def creattag(self,name):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/tags/create?access_token={}".format(token)
        data={   "tag" : {     "name" : name   } } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req=requests.post(url,data=data,headers=headers)
        return req.json()
    
    def gettag(self):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/groups/get?access_token={}".format(token)
        req=requests.get(url)
        return req.json()
    
    def adduser(self,userID,ID):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/tags/members/batchtagging?access_token={}".format(token)
        data={   
                "openid_list" : [ userID],   
                "tagid" : ID
            } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        return req.json()
    
    def getuser(self,ID):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token={}".format(token)
        data={ "tagid" : ID, "next_openid" : "" }
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        return req.json()
    
    def deleteuser(self,userID,ID):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/tags/members/batchuntagging?access_token={}".format(token)
        data={   
                "openid_list" : [ userID],   
                "tagid" : ID
            } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        return req.json()
    
    def usertag(self,user):
        token=get_token()
        url="https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}".format(token,user)
        req = requests.get(url,  headers=headers)
        return req.json()






