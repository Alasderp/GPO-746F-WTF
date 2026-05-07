#!/usr/bin/env python3

# Orange wire connected to GPIO18
# Brown wire to GND

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(18, GPIO.BOTH)

pulses = 0
last = 1
phoneNumber = ''
dialStarted = False
start = 0

'''
When the rotary dial is pulled back, the circuit is complete
The dial is then released and winds down. A switch will open and close during this time.
Count how many times the circuit is interrupted to calculate the number dialled
'''
try:
    while True:
        
        if(dialStarted and (time.time() - start) > 0.5):
            
            if(pulses == 11):
                phoneNumber = phoneNumber + '0'
            else:
                phoneNumber = phoneNumber + str(pulses - 1)

            print("Phone Number: " + phoneNumber)
            dialStarted = False
            pulses = 0
        
        if GPIO.event_detected(18):
            
            current = GPIO.input(18)           

            if(last != current):                      
                if(current != 0):
                    start = time.time()
                    dialStarted = True
                    pulses = pulses + 1
                    time.sleep(0.1)

                last = GPIO.input(18)
                
except KeyboardInterrupt:
    print("Cleaning up pins")
    GPIO.cleanup()
except Exception as e:
    print(e)
    print("Cleaning up pins")
    GPIO.cleanup()
