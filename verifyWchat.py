
import base64
import string
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import xml.etree.ElementTree as ET  
from Crypto.Util.Padding import pad
import socket
import logging
# 配置日志
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

# 创建一个日志器
logger = logging.getLogger(__name__)



class SHA1:
    """计算企业微信的消息签名接口"""   
    
    def getSHA1(self, token, timestamp, nonce, encrypt):
        """用SHA1算法生成安全签名
        @param token:  票据
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            tmp_str = ''.join(sortlist)
            tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
            return   tmp_str
        except Exception as e:
            logger.debug(e)
            print (e)
            return  None
  

class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""   
     
    # xml消息模板   
    AES_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>"""

    def extract(self, xmltext):
        """提取出xml数据包中的加密消息 
        @param xmltext: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt  = xml_tree.find("Encrypt")
            return   encrypt.text
        except Exception as e:
            print (e)
            return  None
    
    def generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        resp_dict = {
                    'msg_encrypt' : encrypt,
                    'msg_signaturet': signature,
                    'timestamp'    : timestamp,
                    'nonce'        : nonce,
                     }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml   
    
 
class PKCS7Encoder():
    """提供基于PKCS7算法的加解密接口"""  
    
    block_size = 32
    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)

        return text + pad * amount_to_pad
    
    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad<1 or pad >32:
            pad = 0
        return decrypted[:-pad]
    
    
class Prpcrypt(object):
    """提供接收和推送给企业微信消息的加解密接口"""
    
    def __init__(self,key):

        #self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式   
        self.mode = AES.MODE_CBC
    
            
    def encrypt(self,text,receiveid):
        """对明文进行加密
        @param text: 需要加密的明文
        @return: 加密得到的字符串
        """      
        # 16位随机字符串添加到明文开头
        random_16B = self.get_random_str().encode('utf-8')
        # 将msg长度转换为4字节的网络字节序
        msg_len_4B = struct.pack("I",socket.htonl(len(text)))
        text = random_16B + msg_len_4B + text.encode('utf-8') + receiveid.encode('utf-8')

        
        # 16位随机字符串添加到明文开头
        # text = self.get_random_str() + struct.pack("I",socket.htonl(len(text))) + text + receiveid
        # 使用自定义的填充方式对明文进行补位填充
        # pkcs7 = PKCS7Encoder()
        # text = pkcs7.encode(text)
        # 使用PKCS7填充方式对明文进行补位填充
        text = pad(text, AES.block_size)

        # 加密    
        cryptor = AES.new(self.key,self.mode,self.key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return  base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:

            print (e)
            return  None
    
    def decrypt(self,text,receiveid):
        """对解密后的明文进行补位删除
        @param text: 密文 
        @return: 删除填充补位后的明文
        """
        try:
            
            cryptor = AES.new(self.key,self.mode,self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text  = cryptor.decrypt(base64.b64decode(text))
            # plain_text = base64.base64_decode(text)

        except Exception as e:
            print (e)
            return None
        try:
            pad = plain_text[-1]
            # 去掉补位字符串 
            #pkcs7 = PKCS7Encoder()
            #plain_text = pkcs7.encode(plain_text)   
            # 去除16位随机字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I",content[ : 4])[0])
            xml_content = content[4 : xml_len+4] 
            from_receiveid = content[xml_len+4:].decode('ascii')

        except Exception as e:
            print (e)
            return  None
        if  from_receiveid != receiveid:
            return None
        return xml_content
    
    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """ 
        rule = string.ascii_letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str)
        
class WXBizMsgCrypt(object):
    #构造函数
    def __init__(self,sToken,sEncodingAESKey,sReceiveId):
        try:
            self.key = base64.b64decode(sEncodingAESKey+"=")  
            assert len(self.key) == 32
        except Exception as e:
            print (e)
            # return ierror.WXBizMsgCrypt_IllegalAesKey,None
        self.m_sToken = sToken
        self.m_sReceiveId = sReceiveId
        
		 #验证URL
         #@param sMsgSignature: 签名串，对应URL参数的msg_signature
         #@param sTimeStamp: 时间戳，对应URL参数的timestamp
         #@param sNonce: 随机串，对应URL参数的nonce
         #@param sEchoStr: 随机串，对应URL参数的echostr
         #@param sReplyEchoStr: 解密之后的echostr，当return返回0时有效
         #@return：成功0，失败返回对应的错误码	

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        sha1 = SHA1()
        signature = sha1.getSHA1(self.m_sToken, sTimeStamp, sNonce, sEchoStr)


        if not signature == sMsgSignature:
            return None
        pc = Prpcrypt(self.key)
        sReplyEchoStr = pc.decrypt(sEchoStr,self.m_sReceiveId)

        return sReplyEchoStr
	
    def EncryptMsg(self, sReplyMsg, sNonce, timestamp = None):
        #将企业回复用户的消息加密打包
        #@param sReplyMsg: 企业号待回复用户的消息，xml格式的字符串
        #@param sTimeStamp: 时间戳，可以自己生成，也可以用URL参数的timestamp,如为None则自动用当前时间
        #@param sNonce: 随机串，可以自己生成，也可以用URL参数的nonce
        #sEncryptMsg: 加密后的可以直接回复用户的密文，包括msg_signature, timestamp, nonce, encrypt的xml格式的字符串,
        #return：成功0，sEncryptMsg,失败返回对应的错误码None     
        pc = Prpcrypt(self.key) 
        encrypt = pc.encrypt(sReplyMsg, self.m_sReceiveId)
        encrypt=f'''yfTdYOeC8B4M90c117AAT8mhsU6+LMyB3v/dxgtI5ceWfXcqndk3mDV4mXYmW2SjOpgBuxttv6it1teVkVZM7SHhC/zU0uvNp2giHoxMQoQunYJabnJYgo8QJKUw/gPmkUt7TmnfEURHzCgvdIhELQmFgEGsQLV4PDSEL6BXnI/rXt8xy6tRVr0nGzzqZdWou+DsXXINtTe89OBqQR6LvnJoYEVB9y+n0fYTm0JK5vwjVOauRHDDgsyhfKQI5hhrxbohrCUB7WRp/Oa5fD+nUGNAoQi8FuANcyLSHzmOLo7cU5oqH6mTkyOWY9DWZGcihWUBFzDDm0PJTo0sxXJdEZJBNIk32A6DvvhNW8PMkP1Z+DXDQz5YOPvbpMuD3YZuPZeNnNYGQnOCg7sz9NtCYic0+/qMVoC/Uj4NmlXtktBfpUvk1ps+0UN3404mizokZXAwjR5IQgI9p5P+plYBGnKuuqnSjrAOagBgWjzWtpNUJTPRV4LTwG/PQCtMoRAd'''

        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名 
        sha1 = SHA1() 

        signature = sha1.getSHA1(self.m_sToken, timestamp, sNonce, encrypt)

        xmlParse = XMLParse()  
        reply=xmlParse.generate(encrypt, signature, timestamp, sNonce)  

        return reply

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        # 检验消息的真实性，并且获取解密后的明文
        # @param sMsgSignature: 签名串，对应URL参数的msg_signature
        # @param sTimeStamp: 时间戳，对应URL参数的timestamp
        # @param sNonce: 随机串，对应URL参数的nonce
        # @param sPostData: 密文，对应POST请求的数据
        #  xml_content: 解密后的原文，当return返回0时有效
        # @return: 成功0，失败返回对应的错误码
         # 验证安全签名 
        xmlParse = XMLParse()
        encrypt = xmlParse.extract(sPostData)

        sha1 = SHA1() 
        signature = sha1.getSHA1(self.m_sToken, sTimeStamp, sNonce, encrypt)

        if not signature == sMsgSignature:
            return None
        pc = Prpcrypt(self.key)
        xml_content = pc.decrypt(encrypt,self.m_sReceiveId)
        root = ET.fromstring(xml_content)
        msg = {}
        for child in root:
            msg[child.tag] = child.text
        return msg

