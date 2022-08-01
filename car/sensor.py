# 使用传感器的模块，用于实现上层应用要求的信息的收集

import RPi.GPIO as GPIO
import smbus
import log
import time
from send_data import send
from threading import Thread
import math
import os
import sys
# 全局变量，保存各种传感器的位置信息
temsensor=""
start_time = time.time()


pcf = 0x48
tem = 0x40
light = 0x41
# 开启总线
bus = smbus.SMBus(1)

# 一个供外部调用的函数,用来收集各个传感器的数据
# times代表每隔多久收集一次数据

def callsensor(senname="all", stoptime="",Time=10):
    log.init_logging("sensor.log")
    start_time = time.time()
    stoptime = time.strptime(stoptime, "%Y-%m-%d %H:%M:%S")
    stoptime = time.mktime(stoptime)
    current_time = time.time()
    while(current_time <= stoptime):
        if(int(current_time - start_time) % Time == 0):
            if senname == "all":
                tem = tem_sensor()
                sendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                data = {"temper":str(tem), "datet":sendtime, "cid":'1'}
                log.write_tolog("collected data and asked for send")
                t = Thread(target=send, args=(data, "Temper"))
                t.start()
                t.join()
                voi = light_sensor()
                sendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                data = {"voice":str(voi), "datet":sendtime, "cid":'1'}
                log.write_tolog("collected data and asked for send")
                t = Thread(target=send, args=(data, "Voice"))
                t.start()
                t.join()
            elif senname =="temper":
                tem = tem_sensor()
                sendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                data = {"temper":str(tem), "datet":sendtime, "cid":'1'}
                log.write_tolog("collected data and asked for send")
                t = Thread(target=send, args=(data, "Temper"))
                t.start()
                t.join()
            elif senname== "voice":
                voi = light_sensor()
                sendtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                data = {"voice":str(voi), "datet":sendtime, "cid":'1'}
                log.write_tolog("collected data and asked for send")
                t = Thread(target=send, args=(data, "Voice"))
                t.start()
                t.join()
            time.sleep(3)
        current_time = time.time()
    # 计时结束，退出本线程
    exit()


# 获取当前的温度值
def tem_sensor():
    sum = 0
    for i in range(5):
        # 向pcf8591写入此控制指令，代表要从其对应的寄存器中读数据
        bus.write_byte(pcf, tem)
        # 此时读出的便是ain0端口获取的数据
        value = 5*(255-float(bus.read_byte(pcf)))/255
        value = (5-value) * 10000 / value
        value = 1/(((math.log(value/10000))/3950)+(1/(273.15+25)))
        value = value - 273.15
        sum+=value
    return sum / 5
# 获取当前的亮度值
def light_sensor():
    sum = 0
    for i in range(5):
        bus.write_byte(pcf, light)
        sum += float(bus.read_byte(pcf))
    return sum/5

