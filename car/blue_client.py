import hashlib
import socket
import log
import os
import shutil
# 创建客户端套接字，套接字传输方式为蓝牙，数据收发模式为流式传输，套接字所使用的具体蓝牙协议为RFCOMM
client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
log.init_logging("client.log")
# 正式与服务器端创建连接
def con_s():
    global client
    # 连接到对方的蓝牙地址、蓝牙端口
    if(client.connect_ex(("DC:A6:32:F0:67:9B", 4)) == False):
        log.write_tolog("connection faild, trying reconect", "warning")
        con_s()
    else:
        log.write_tolog("successfuly connected to nearby car")

def send_data(filename):
    global client
    # 用于发送调用本模块的模块要求发送的文件
    if os.path.exists(filename+".send"):os.remove(filename+".send")
    shutil.copy(filename, filename+".send")
    os.system("python3 rsa.py --ef {} server.pub".format(filename+".send"))
    size = 0
    f = open(filename+".send", "rb")
    for line in f:
        size+=len(line)
    f.close()
    name = filename.split("/")[1]
    cmd = "send#{}#{}".format(name+".send", size)
    os.system("python3 rsa.py --es {} client.pri".format(cmd))
    f = open("tmpfile/tmp", 'r')
    cmd = str(f.readline())
    f.close()
    # 发送文件的头
    client.send(cmd.encode(encoding='utf-8'))
    log.write_tolog("send file head to another car")
    buf = client.recv(512).decode('utf-8')
    # 知晓服务器已经转向接收文件本身的状态
    if buf == "recv":
        # 正式开始发送文件本身，首先对文件进行加密        
        f = open(filename+".send", "rb")
        for line in f:
            client.send(line)
        f.close()
        log.write_tolog("send success")
    # 服务器没有转向发送的状态
    else:log.write_tolog("send faild", "error");return False
    buf = client.recv(512).decode('utf-8')
    if(buf == "recvfin"):
        with open(filename+".send", "rb") as f:
            c = "md5#{}".format(hashlib.md5(f.read()).hexdigest())
        log.write_tolog("sending md5 for check")
        os.system("python3 rsa.py --es {} client.pri".format(c))
        f.close()
        f = open("tmpfile/tmp", 'r')
        c = str(f.readline())
        f.close()
        client.send(c.encode(encoding='utf-8'))
    buf = client.recv(512).decode(encoding='utf-8') 
    # 文件接收是否正确，错误则重发
    if(buf  == "resend"):
        log.write_tolog("faild to send file for wrong md5, already resend")
        send_data(filename)
    elif(buf == "success"):
        # 关闭当前套接字
        client.close()
        # 重新创建套接字，方便之后的发送
        client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        log.write_tolog("already ask another car to send file")
        return True
    


