import hashlib
import time
from xml.etree import ElementTree
from flask import Flask, request, make_response, jsonify,render_template
import threading
import wechat as ult
from flask_cors import CORS
from wechat import config   # 从wechat文件夹中导入config.py文件
from wechat import loger


app = Flask(__name__)
CORS(app)
logger = loger.setup_logger(__name__)
clt=ult.clt()
wx_token = config.wx_token
default_reply = config.default_reply


@app.route('/', methods=['GET'])
def index():
    return jsonify({'code': 200, 'data': 'success'})


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    # 微信服务器会发送两种类型的请求，一种是GET请求，一种是POST请求
    # GET请求用于验证服务器地址的有效性
    # POST请求用于接收微信服务器转发过来的用户发送的消息
    # 下面的代码分别处理这两种请求
    if request.method == 'GET' and  verify_server_url(request):
        # 验证服务器地址的有效性
        echostr = request.args.get('echostr')
        return make_response(echostr)


    elif request.method == 'POST' and verify_server_url(request):
        # 处理POST请求
        xml_data = request.data
        msg = parse_message(xml_data)
        user = msg["FromUserName"]
        msg_type = msg["MsgType"]
        # 这个是菜单点击事件的处理。
        if msg_type == "event" and msg["Event"] == "CLICK":
            if msg["EventKey"] == "yourID":
                return make_response(build_text_response(msg, user))
            return make_response(build_text_response(msg, "天王盖地虎"))
        # 这是处理用户发送的文本消息的代码。
        if msg_type == "text" :
            cont=msg["Content"]
            if cont=="清除":
                clt.clean_usermsg(user)
                return make_response(build_text_response(msg, "记忆清除成功"))
            else:
                message,model=clt.deal_msg(user,cont)
                thread = threading.Thread(target=clt.send_text, args=(user, message, model))
                thread.start()
                return make_response(build_text_response(msg, default_reply))
        return jsonify({'code': 200, 'data': 'success'})



# 验证服务器地址的有效性
def verify_server_url(request):
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    token = wx_token  
    tmp_arr = [token, timestamp, nonce]
    tmp_arr.sort()
    tmp_str = ''.join(tmp_arr)
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    if tmp_str == signature:
        return True
    else:
        return False


# 解析微信服务器发送过来的XML数据
def parse_message(xml_data):
    root = ElementTree.fromstring(xml_data)
    msg = {}
    for child in root:
        msg[child.tag] = child.text

    return msg


# 构造回复给用户的文本消息
def build_text_response(msg, content):
    resp_msg = f"""
        <xml>
        <ToUserName><![CDATA[{msg['FromUserName']}]]></ToUserName>
        <FromUserName><![CDATA[{msg['ToUserName']}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>
    """
    return resp_msg



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=34568, threaded=True)

# port=34568是端口号，可以自己设置，但是要注意不要和其他端口号冲突。

