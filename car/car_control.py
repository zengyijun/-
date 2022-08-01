from curses.ascii import TAB
import RPi.GPIO as GPIO
import time
import sys
import log
from send_data import send
from threading import Thread

Speed:int
L_Motor = None
R_Motor = None
red_R = 16
red_L = 12
PWMA = 18
AIN1 = 22
AIN2 = 27
PWMB = 23
BIN1 = 25
BIN2 = 24
BtnPin = 19
Gpin = 5
Rpin = 6

# 初始化小车的各个参数
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Gpin, GPIO.OUT)
    GPIO.setup(Rpin, GPIO.OUT) 
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(red_R,GPIO.IN)
    GPIO.setup(red_L,GPIO.IN)
    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)
    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)

# 用于小车的控制。本函数是初始化函数
def init_car(direction, T, L, R):
    global Speed, L_Motor, R_Motor
    setup()
    Speed = 50
    L_Motor = L
    print(L)
    R_Motor = R
    L_Motor.start(0)
    R_Motor.start(0)
    R_ = GPIO.input(red_R)
    L_ = GPIO.input(red_L)
    if direction == "left":
        if L_ == True:
            turn_left(T/4)
    elif direction == "front":
        if L_ and R_ == True:
            turn_up(T)
    elif direction == "back":
        turn_down(T)
    elif direction == "right":
        if R_ == True:
            turn_right(T/4)


def turn_left(T):
    global L_Motor, Speed, R_Motor
    L_Motor.ChangeDutyCycle(Speed*0.375)
    GPIO.output(AIN2, True)
    GPIO.output(AIN1, False)
    R_Motor.ChangeDutyCycle(Speed*0.25)
    GPIO.output(BIN2, False)
    GPIO.output(BIN1, True)
    time.sleep(T)
def turn_right(T):
    global L_Motor, Speed, R_Motor
    L_Motor.ChangeDutyCycle(Speed*0.25)
    GPIO.output(AIN2, False)
    GPIO.output(AIN1, True)
    R_Motor.ChangeDutyCycle(Speed*0.375)
    GPIO.output(BIN2, True)
    GPIO.output(BIN1, False)
    time.sleep(T)
def turn_up(T):
    global L_Motor, Speed, R_Motor
    L_Motor.ChangeDutyCycle(Speed)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1
    R_Motor.ChangeDutyCycle(Speed)
    GPIO.output(BIN2,False)#BIN2
    GPIO.output(BIN1,True) #BIN1
    time.sleep(T)
def turn_down(T):
    global L_Motor, Speed, R_Motor
    L_Motor.ChangeDutyCycle(Speed)
    GPIO.output(AIN2,True)#AIN2
    GPIO.output(AIN1,False) #AIN1
    R_Motor.ChangeDutyCycle(Speed)
    GPIO.output(BIN2,True)#BIN2
    GPIO.output(BIN1,False) #BIN1
    time.sleep(T)