import json
import blue_client
import requests
import pywifi
import log
import sys
from threading import Thread
# https请求头
headers = {'content-type':'application/json', 'connection':'close'}
# data代表数据字典、local代表接收方对应的url地址
def send(data, local):
    log.init_logging("sender.log")
    t = None
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()
    # WiFi已连接，直接通过WiFi发送
    if((iface[0].status() == pywifi.const.IFACE_CONNECTED) or (iface[1].status() == pywifi.const.IFACE_CONNECTED)):
        t = Thread(target=send_http, args=(data, local))
        log.write_tolog("send data directly")
        t.setDaemon(True)
        t.start()
    # WiFi未连接，通过蓝牙发送
    else:
        log.write_tolog("ask another car to send")
        send_blue(local, data)
        

# 通过蓝牙发送数据的接口函数，传入的参数是一个文本文件的文件名
# t代表发送的类型；data代表文件的数据域
def send_blue(t, data):
    # 在此处打包json文件
    # 添加一项数据域，表示此条消息的发送状态
    data.update({"remark":"send by bluetooth"})
    filename = "tmpfile/"+t
    # 循环写入字典数据
    with open(filename,'w') as f:
        for i in data.keys():
            f.write(str(i+"#"+data[i]+"\n"))
    log.write_tolog("calling function to send")
    # 调用蓝牙连接模块连接
    blue_client.con_s()
    log.write_tolog("send success")
    # 数据正式发送
    t = Thread(target=blue_client.send_data, args=(filename,))
    t.start()
    t.join()
    
# 蓝牙接口，调用此接口函数通过http进行发送
def blue_https(filename):
    log.init_logging("sender.log")
    # 解析传入的文件路径，获取隐藏在其中的url值
    type = filename.split('/')[1]
    type = type.split('.')[1]
    data = {}
    # 将文件中的内容读入到数据字典中去
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.replace('\n', "")
            line = line.split(':')
            data.update({line[0]:line[1]})
    log.write_tolog("successfully helped!")
    # 调用发送函数进行发送
    send_https(data, type)


    

# 通过https发送数据的接口函数，传入的参数是字典，可以json结构体化发送
def send_https(data, type):
    url = "https://lot.cpolar.io/"+type
    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    res = requests.post(url=url, data=data, headers=headers)
    if(res.status_code == 200):log.write_tolog("send data success")
    else:log.write_tolog("can't send", "error")
    sys.exit()

    