# 接收信息的模块。此模块接收客户端传来的各种json报文，并对其处理
# 按照要求进行相应
import requests
import json
import RPi.GPIO as GPIO
import setup
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib import response
from sensor import callsensor
from cam import init_cam
from threading import Thread
import log
import time
from car_control import init_car
import serial
import send_data



def gps_req(start_time):
    log.init_logging("gps.log")
    port = "/dev/ttyUSB0"
    ser = serial.Serial(port, 9600)
    current_time = time.time()
    # 每10秒获取一次数据，之后发送
    while True:
        if ((int(current_time - start_time) % 10) == 0):
            sendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
            ori_datas = ser.readline().decode("utf-8")
            ori_datas = ori_datas.replace("\r\n","")
            data = ori_datas.split(",")
            if("GGA" in data[0]) and (data[2]!="") and (data[4]!=""):
                log.write_tolog("send current location")
                x = float(data[4][0:3])+(float(data[4][3:])/60)
                y = float(data[2][0:2])+(float(data[2][2:])/60)
                req = requests.get("https://api.map.baidu.com/geoconv/v1/?coords=%s&from=1&to=5&ak=pl1KAu7wP0k2QlClDTb71CGPFV4W3nul"%(str(str(x)+","+str(y))))
                x_y = json.loads(req.text)
                data = {"x":x_y["result"][0]["x"], "y":x_y["result"][0]["y"], "datet":sendtime, "cid":"1"}
                t = Thread(target=send_data.send, args=(data, "Gps"))
                t.setDaemon(False)
                log.write_tolog("send success")
                t.start()
                t.join()
                time.sleep(1)
            else:time.sleep(1);continue
        current_time = time.time()

host = ('0.0.0.0', 8888)
L_Motor = None
R_Motor = None
current_car_thread = None
current_cam_thread = None
class Request(BaseHTTPRequestHandler):
    t = None
    def do_POST(self):
        # 全局变量：t、current_car_thread、current_cam_thread
        # 保存当前的小车行走线程、摄像头线程的名称
        global t, current_car_thread, current_cam_thread
        log.write_tolog("get request")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        dic = json.loads(post_data)
        self.send_response(200)
        if (dic['op'] == "stop"):
            if current_car_thread !=None:
                L_Motor.stop(0)
                R_Motor.stop(0)
                if current_car_thread.is_alive():
                    SystemExit(current_car_thread)
        elif(dic['op'] == 'car'):
            log.write_tolog("request type is car")
            t = Thread(target=init_car, args=(dic['type'], 50, 1000, L_Motor, R_Motor))
            current_car_thread = t
            t.start()

        elif(dic['op'] == 'cam'):
            log.write_tolog("request type is cam")
            if (current_cam_thread != None):
                if(current_cam_thread.is_alive()):
                    return
            t = Thread(target=init_cam, args=(dic['type'],))
            current_cam_thread = t
            t.setDaemon(False)
            t.start()
        elif(dic['op'] == 'sensor'):
            log.write_tolog("request type is sensor")

            t = Thread(target=callsensor, args=(dic['type'], dic['stop_time'], int(dic['time'])))
            t.setDaemon(False)
            t.start()
        else: self.send_error(500);log.write_tolog("request type")
        
             

class ThreadingHttpServer( ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    t = Thread(target=gps_req, args=(time.time(),))
    t.setDaemon(True)
    t.start()
    setup.setup()
    L_Motor = GPIO.PWM(18, 100)
    R_Motor = GPIO.PWM(23, 100)
    log.init_logging("request.log")
    server = ThreadingHttpServer(host, Request)
    server.serve_forever()
    server.server_close()
