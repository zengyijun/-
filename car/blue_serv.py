import hashlib
import socket
import send_data
import log
import threading # 多线程处理连接
import os

# 一些用于文件接收的全局变量
isRecving = False # 判断是否正在接收文件
fileName="tmpfile/" # 接收到的文件的文件名
fileSize = 0 # 文件的总大小
recvSize = 0 # 累计已接收的大小
file= None
# 创建一个套接字，连接类型是蓝牙，连接的数据包发送时连续可靠，具体使用的蓝牙协议时RFCOMM
server_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_socket.bind((socket.BDADDR_ANY, 4))
server_socket.listen(1)

# 日志模块，用于将连接信息输出到日志文件中
log.init_logging("blue_server.log")

# 服务处理函数
def serv_client(sock, addr):
    # 几个全局变量，第一个标识本函数是否等待循环接收文件、第二个标识当前所接收文件的文件名；
    # 第三个用于标识当前要接收的文件的文件大小；第四个是一个文件描述符，用于将收到的文件部分字节流写入文件中
    global isRecving, fileName, fileSize, recvSize, file
    while True:
        # 此时说明发送的是文件名和文件大小
        if(isRecving == False):
            buf = sock.recv(512)
            if not buf: exit()
            # 对接收到的数据进行解码
            buf = buf.decode(encoding='utf-8')
            log.write_tolog("recv file head from {}, checking its digital sign".format(addr))
            # 首先对buf进行数字签名认证
            os.system("python rsa.py --ds {} client.pub".format(buf))
            tmpfile = open("tmpfile/tmp", 'r')
            buf = str(tmpfile.read())
            tmpfile.close()
            buf = buf.split('#')
            # 当前对方发送的字符串中标志此字符串中含有文件名信息
            if(buf[0] == 'send'):
                fileName = "tmpfile/"+buf[1]
                file = open(fileName, 'wb')
                fileSize = int(buf[2])
                recvSize = 0
                isRecving = True # 此处开始接收文件
                log.write_tolog("the client send a file: {}, hope us help sending it to server".format(buf[1]))
                sock.send("recv".encode(encoding='utf-8'))  
            elif(buf[0] == "md5"):
                # 此处校验接收到的文件的md5值
                # 校验方式是对比两个数字签名
                log.write_tolog("recv finished, checking its md5 number")
                f = open(fileName, 'rb')
                md5_s = hashlib.md5(f.read()).hexdigest()
                f.close()
                if md5_s == buf[1]:
                    sock.send("success".encode(encoding='utf-8'))
                    log.write_tolog("already checked its md5. file name is {}. file is now saved.".format(addr, fileName))
                    os.system("python rsa.py --df {} server.pri".format(fileName))
                    log.write_tolog("already checked its md5. file: {}, owner: {}. file is now saved.".format(fileName.split("/")[1], addr))
                    # 以子线程的方式调用send_data中的相应接口函数
                    t = threading.Thread(targets=send_data.blue_https, args=(fileName, ))
                    t.setDaemon(False)
                    t.start()
                    # 等待子线程发送结束
                    t.join()
                    # 退出本服务线程
                    exit()   
                else:
                    # md5值不正确，让对方重发
                    sock.send("resend".encode(encoding='utf-8'))
                    log.write_tolog("file from {} was error for wrong md5. Already ask for resend".format(addr),"error") 
            # 无法识别对方发送的字符串，让对方重发  
            else:
                sock.send("resend".encode(encoding='utf-8'))   
        # 文件的循环接收部分 
        else:
            if(fileSize - recvSize > 512):
                buf = sock.recv(512)
                file.write(buf)
                recvSize += len(buf)
            else:
                log.write_tolog("recv file {} succeed".format(fileName.split('/')[1]))
                sock.send("recvfin".encode(encoding='utf-8'))
                buf = sock.recv(fileSize - recvSize)
                file.write(buf)
                isRecving = False
                file.close()

              

# 对连接进行监听
while(True):
    sock, addr = server_socket.accept()
    log.write_tolog("accept connection from %s"%(addr[0]))
    t = threading.Thread(target=serv_client, args=(sock, addr[0]))
    t.setDaemon(True)
    t.start()

