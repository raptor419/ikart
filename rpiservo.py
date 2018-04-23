import RPi.GPIO as GPIO
import time
import numpy
GPIO.setmode(GPIO.BOARD)
GPIO.setup(03, GPIO.OUT)
GPIO.setup(05, GPIO.OUT)
pwm1=GPIO.PWM(03, 50)
pwm1.start(0)
pwm2=GPIO.PWM(05, 50)
pwm2.start(0)
def SetAngle1(angle):
    duty = angle / 18 + 2
    GPIO.output(03, True)
    pwm1.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(03, False)
    pwm1.ChangeDutyCycle(0)
def doa1():
    SetAngle1(90)
    time.sleep(2)
    SetAngle1(0)
    time.sleep(2)
def SetAngle2(angle):
    duty = angle / 18 + 2
    GPIO.output(05, True)
    pwm2.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(05, False)
    pwm2.ChangeDutyCycle(0)
def doa2():
    SetAngle2(0)
    time.sleep(2)
    SetAngle2(90)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    input_state1 = GPIO.input(12)
    if input_state1 == False:
        print('Button 1 Pressed')
        doa1()
        time.sleep(1)
    input_state2 = GPIO.input(18)
    if input_state2 == False:
        print('Button 2 Pressed')
        doa2()
        time.sleep(1)
pwm1.stop()
pwm2.stop()
GPIO.cleanup()
