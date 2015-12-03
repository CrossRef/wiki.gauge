#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import requests
import threading

pwm = PWM(0x40)
servoMin = 160  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

citation_min = 0
citation_max = 360

value = 500
current_value = 150
step = 10

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)


def fetch_loop():
  global value
  while True:
    print("Fetch")
    last_val = requests.get("http://wikipedia.labs.crossref.org/status").json()['citation-history'][0]
    per_hour = min(last_val * 12, servoMax)
    value = (per_hour / citation_max)  * (servoMax - servoMin) + servoMin
    print("Value %d" % value)
    time.sleep(60)

def run_background():
  thread = threading.Thread(target=fetch_loop)
  thread.start()

def run():
  global value, current_value
  pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
  while (True):
    diff = value - current_value
    print str(current_value) + " DIFF " + str(diff)
    if diff > step:
      current_value += step
    elif diff < -step:
      current_value -= step 

    pwm.setPWM(0, 0, current_value)
    time.sleep(0.2)



run_background()
run()


