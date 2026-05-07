#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

from CradleSwitch import CradleSwitch
from RotaryDial import RotaryDial

cradleSwitch = CradleSwitch()
rotaryDial = RotaryDial()


global callIncoming
callIncoming = False

def button_A_callback(channel):
    print("Button A was pushed")
    global callIncoming
    callIncoming = True
    
def button_B_callback(channel):
    print("Button B was pushed")
    global callIncoming
    callIncoming = False

try:

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    #Button A on the Clipper LTE Hat
    GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(5, GPIO.FALLING, callback=button_A_callback, bouncetime=200)
    #Button B on the Clipper LTE Hat
    GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=button_B_callback, bouncetime=200)

    while True:
        
        time.sleep(1)
        
        #Handset not lifted and no call incoming. Do nothing.
        if(not cradleSwitch.isHandsetLifted() and not callIncoming):
            print("No call incoming, Line is free (Handset Not Lifted)")
            
            
        #Handset lifted and no call incoming. Prepare to read from rotary dial.    
        elif(cradleSwitch.isHandsetLifted() and not callIncoming):
            print("No call incoming, Line already busy (Handset Lifted)")
            print(rotaryDial.dialingStarted())
            #Make async call to rotary dial and prepare to read in a telephone number
            #Then wait until dialling complete or handset returned to cradle
            
            
        #Handset not lifted and call incoming. Ring the bells until handset lifted or call is dropped.    
        elif(not cradleSwitch.isHandsetLifted() and callIncoming):
            print("Call incoming, Line is free (Handset Not Lifted)")
            
            
        #Handset  lifted and call incoming. Do nothing as line is already busy.    
        elif(cradleSwitch.isHandsetLifted() and callIncoming):
            print("Call incoming, Line already busy (Handset Lifted)")
        
      
except KeyboardInterrupt:
    print("Cleaning up pins")
    GPIO.cleanup()
except Exception as e:
    print(e)
    print("Cleaning up pins")
    GPIO.cleanup()
finally:
    print("Cleaning up pins")
    GPIO.cleanup()