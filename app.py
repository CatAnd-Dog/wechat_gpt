from urllib.parse import unquote
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import verifyWchat
import wechat as ult
import threading


app = Flask(__name__)
CORS(app)

sToken = ult.wx_token
sEncodingAESKey=ult.EncodingAESKey
sCorpID=ult.appid
wxcpt=verifyWchat.WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)


clt=ult.clt()

@app.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'data': 'success'})


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    sVerifyMsgSig=request.args.get('msg_signature')
    sVerifyTimeStamp=request.args.get('timestamp')
    sVerifyNonce=request.args.get('nonce')
    sVerifyMsgSig= unquote(sVerifyMsgSig) if sVerifyMsgSig else None
    sVerifyTimeStamp= unquote(sVerifyTimeStamp) if sVerifyTimeStamp else None
    sVerifyNonce= unquote(sVerifyNonce) if sVerifyNonce else None

    # GET请求用于验证服务器地址的有效性
    if request.method == 'GET' :
        # 验证服务器地址的有效性
        sVerifyEchoStr=request.args.get('echostr')
        sVerifyEchoStr = unquote(sVerifyEchoStr) if sVerifyEchoStr else None
        sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
        return make_response(sEchoStr)


    elif request.method == 'POST' :
        # 处理POST请求
        xml_data = request.data
        msg=wxcpt.DecryptMsg( xml_data, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce)
        user = msg["FromUserName"]
        msg_type = msg["MsgType"]
        agentid=msg["AgentID"]
        if msg_type == "text" :
            cont=msg["Content"]
            thread = threading.Thread(target=clt.send_text, args=(user, cont,agentid))
            thread.start()
        
        # 自动回复消息未解决
        return ''





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=34568, threaded=True)

# port=34568是端口号，可以自己设置，但是要注意不要和其他端口号冲突。


