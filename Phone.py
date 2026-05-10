#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading
import pygame

from CradleSwitch import CradleSwitch
from RotaryDial import RotaryDial

cradleSwitch = CradleSwitch()
rotaryDial = RotaryDial()


global callIncoming
callIncoming = False

global callOutgoing
callOutgoing = False

def button_A_callback(channel):
    global callIncoming
    callIncoming = not callIncoming
    print("Button A was pushed, incoming call flag set to: " + str(callIncoming))
    
def button_B_callback(channel):
    global callOutgoing
    callOutgoing = not callOutgoing
    print("Button B was pushed, outgoing call flag set to: " + str(callOutgoing))

try:

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    #Button A on the Clipper LTE Hat
    GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(5, GPIO.FALLING, callback=button_A_callback, bouncetime=200)
    #Button B on the Clipper LTE Hat
    GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=button_B_callback, bouncetime=200)
    
    pygame.mixer.init()

    while True:
                
        time.sleep(0.1)
            
        #Handset lifted and no call incoming. Prepare to read from rotary dial.    
        if(cradleSwitch.isHandsetLifted() and not callIncoming):
            print("Handset lifted, no call incoming, ready to dial out")
            
            pygame.mixer.music.load("./MiscDocs/Sound Effects/UK_dial_tone.mp3")
            
            #Play the dial tone
            pygame.mixer.music.play(-1)
            
            #Create rotary dial thread and prepare to read in a telephone number
            rotaryDial = RotaryDial() 
            dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(True,))
            dialThread.start()
            
            #Then wait until dialling complete/timed-out or handset returned to cradle
            while(dialThread.is_alive() and cradleSwitch.isHandsetLifted()):
                time.sleep(0.1)
                #TODO - Set flag to only execute this if statement once when sending AT command
                if(rotaryDial.isDialingStarted()):
                    pygame.mixer.music.stop()
        
            rotaryDial.endListening()
        
            #If a number was dialled, do something with it.
            #Else play a message telling user to hang-up and re-dial
            if(rotaryDial.getPhoneNumber()):
                print("Phone Number dialled: " + rotaryDial.getPhoneNumber())
                
                #Initiate an outgoing all here
                
                #Create another dial thread in case presented with an in-call menu
                rotaryDial = RotaryDial() 
                dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(False,))
                dialThread.start()
                
                while(callOutgoing and cradleSwitch.isHandsetLifted()):
                    time.sleep(0.1)
                    #If a number was dialed, send this via AT command and spawn new dial thread
                    if(not dialThread.is_alive()):
                        print("In-call Number dialled: " + rotaryDial.getPhoneNumber())
                        rotaryDial = RotaryDial() 
                        dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(False,))
                        dialThread.start()                                    
            else:             
                #If Dialling not started play an error message
                print("Playing off-hook message until handset replaced")
                pygame.mixer.music.load("./MiscDocs/Sound Effects/OffHookMessage.mp3")
                pygame.mixer.music.play(-1)
            
            print("Out-going call ended or dialling timed-out, waiting for handset to be replaced")
            
            rotaryDial.endListening()
            cradleSwitch.waitForHandsetReplacement()
            pygame.mixer.music.stop()
            print("Handset replaced after call")
            
                            
            
        #Handset not lifted and call incoming. Ring the bells until handset lifted or call is dropped.    
        elif(not cradleSwitch.isHandsetLifted() and callIncoming):
            
            print("Call incoming, line is free (Handset Not Lifted)")
            
            #Ring bell for as long as there is an incoming call and handset not lifted
            pygame.mixer.music.load("./MiscDocs/Sound Effects/british_phone_bell.mp3")
            pygame.mixer.music.play(-1)
    
            while not cradleSwitch.isHandsetLifted() and callIncoming:
                time.sleep(0.1)
            
            pygame.mixer.music.stop()
            
            #Wait until phone is hung-up or call has ended
            while cradleSwitch.isHandsetLifted() and callIncoming:
                time.sleep(0.1)
            
            print("Incoming call ended, waiting for handset to be replaced")
            cradleSwitch.waitForHandsetReplacement()
            print("Handset replaced after call")
            
        
      
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