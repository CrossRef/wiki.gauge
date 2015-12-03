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

value = servoMin
current_value = servoMin
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
  """Fetch the most recent 5-minute bucket in a loop"""

  global value
  while True:
    try:
      print("Fetch")
      # Get the second bucket, as the first one constantly changes.
      history = requests.get("http://wikipedia.labs.crossref.org/status").json()['citation-history']
      last_val = history[1]
      print("History")
      print(history)
      per_hour = min(last_val * 12, servoMax)
      proportion = (per_hour / float(citation_max))
      value = proportion  * (servoMax - servoMin) + servoMin
      print("Last value: %d, per hour: %d, proportion: %f, value: %d" % (last_val, per_hour, proportion, value))
    except Exception, e:
      # If we get an error fetching ignore and try again next time. This will happen first time as the network is coming up.
      print("Error %s" % e)
    
    # Bucket is updated every 5 minutes. Fetch every minute to minimise aliasing.
    time.sleep(60)

def run_background():
  """Run the background data fetch loop"""

  thread = threading.Thread(target=fetch_loop)
  thread.start()

def run():
  """Take the current value and gently converge on it"""

  global value, current_value
  pwm.setPWMFreq(60)
  while (True):
    diff = value - current_value
    if diff > step:
      print(str(current_value) + " DIFF " + str(diff))
      current_value += step
    elif diff < -step:
      print(str(current_value) + " DIFF " + str(diff))
      current_value -= step 

    pwm.setPWM(0, 0, current_value)
    time.sleep(0.2)

run_background()
run()


