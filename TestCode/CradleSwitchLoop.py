#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPIO 21 set as input, pulled up and connected to T3 terminal of phone
#GND pin connected to T6 terminal of phone
GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_UP)

try:
    while True:
        
        if GPIO.input(21) == False:
            print("Handset is lifted from cradle")
        elif GPIO.input(21) == True:
            print("Handset is placed on cradle")
            
        time.sleep(0.5)        
    
except KeyboardInterrupt:
    print("Cleaning up pins")
    GPIO.cleanup()
except Exception as e:
    print(e)
    print("Cleaning up pins")
    GPIO.cleanup()            
        
