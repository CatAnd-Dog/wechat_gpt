import requests
import json
from . import config

# 这个是管理用户标签，用来限制用户可以使用的功能

headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }


class taguser:
    def __init__(self):
        self.display_error=config.display_error

    def edittag(self,id,name,token):
        url="https://api.weixin.qq.com/cgi-bin/tags/update?access_token={}".format(token)
        data={   "tag" : {    "id" : id,     "name" : name  } } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        req=self.display_error(req)
        return req.json()
    
    def creattag(self,name,token):
        url="https://api.weixin.qq.com/cgi-bin/tags/create?access_token={}".format(token)
        data={   "tag" : {     "name" : name   } } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req=requests.post(url,data=data,headers=headers)
        req=self.display_error(req)
        return req.json()
    
    def gettag(self,token):
        url="https://api.weixin.qq.com/cgi-bin/tags/get?access_token={}".format(token)
        req=requests.get(url)
        req=self.display_error(req)
        return req.json()
    
    def adduser(self,userID,ID,token):
        url="https://api.weixin.qq.com/cgi-bin/tags/members/batchtagging?access_token={}".format(token)
        data={   
                "openid_list" : [ userID],   
                "tagid" : ID
            } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        req=self.display_error(req)
        return req.json()
    
    def getuser(self,ID,token):
        url="https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token={}".format(token)
        data={ "tagid" : ID, "next_openid" : "" }
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        req=self.display_error(req)
        return req.json()
    
    def deleteuser(self,userID,ID,token):
        url="https://api.weixin.qq.com/cgi-bin/tags/members/batchuntagging?access_token={}".format(token)
        data={   
                "openid_list" : [ userID],   
                "tagid" : ID
            } 
        data=json.dumps(data, ensure_ascii=False).encode('utf8')
        req = requests.post(url, data=data, headers=headers)
        req=self.display_error(req)
        return req.json()
    
    def usertag(self,user,token):
        url="https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}".format(token,user)
        req = requests.get(url,  headers=headers)
        req=self.display_error(req)
        return req.json()


