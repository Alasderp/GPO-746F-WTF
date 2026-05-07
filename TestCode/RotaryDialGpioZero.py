#!/usr/bin/env python3

# Orange wire connected to GPIO14
# Brown wire to GND

import time
from gpiozero import Button

orangeSwitch = Button(14)

pulses = 0
last = 1
phoneNumber = ''
dialStarted = False
start = 0

try:
    while True:
        if(dialStarted and (time.time() - start) > 1):
            
            if(pulses == 11):
                phoneNumber = phoneNumber + '0'
            else:
                phoneNumber = phoneNumber + str(pulses - 1)

            print("Phone Number: " + phoneNumber)
            dialStarted = False
            pulses = 0
        
        if orangeSwitch.is_pressed:
            
            #print("dial pressed" + str((time.time() - start)))

            current = orangeSwitch.is_active
            
            print("orange value" + str(orangeSwitch))
            
            if(last != current):              
                if(current != 0):
                    start = time.time()
                    dialStarted = True
                    pulses = pulses + 1
                    time.sleep(0.1)

                last = orangeSwitch.is_active
                
except KeyboardInterrupt:
    print("Keyboard Interruption")
except Exception as e:
    print(e)
