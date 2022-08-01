import RPi.GPIO as GPIO
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
    # GPIO.setup(Gpin, GPIO.OUT)
    # GPIO.setup(Rpin, GPIO.OUT) 
    # GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # GPIO.setup(red_R,GPIO.IN)
    # GPIO.setup(red_L,GPIO.IN)
	
    # GPIO.setup(AIN2,GPIO.OUT)
    # GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMA,GPIO.OUT)

    # GPIO.setup(BIN1,GPIO.OUT)
    # GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(PWMB,GPIO.OUT)

    