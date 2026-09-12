#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading
import pygame

from CradleSwitch import CradleSwitch
from RotaryDial import RotaryDial
from SerialProducerConsumer import SerialProducerConsumer

cradleSwitch = CradleSwitch()
rotaryDial = RotaryDial()
diallingStartedLock = threading.Lock()
endListeninglock =  threading.Lock()

def button_A_callback(channel):
    print("Button A was pushed")
    
def button_B_callback(channel):
    print("Button B was pushed")
    
    
def isCallIncoming(lineString):
    callStatus = lineString.split(":")[1].split(",")[2]
    print("\nCall status: " + callStatus + "\n")
    if callStatus == "4":
        return True
    return False

    
pc = SerialProducerConsumer('/dev/ttyS0', 115200)
pc.start()

atCommandPlayDialTone = 'AT+STTONE=1,20,15000\r\n'
atCommandPlayOffHook = 'AT+STTONE=1,7,15000\r\n'
atCommandStopAudio = "AT+STTONE=0\r\n"

atCommandDialOut = "ATD{0};\r\n"
atCommandAnswerCall = "ATA\r\n"
atCommandHangUp = "AT+CHUP\r\n"

atCommandListCalls = "AT+CLCC\r\n"

atCommmandSendDTMF = 'AT+VTS="{0}"\r\n'

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
    
    pygame.mixer.init()
    
    while True:
                
        time.sleep(0.1)
        
        data = pc.receive()
        
        if data:
            for lineBytes in data:
                lineString = lineBytes.decode("utf-8")
                print(lineString)
               
                if lineString.find("VOICE CALL: START") != -1:
                    print("\nOutgoing call initiated\n")
                elif lineString.find("VOICE CALL: END") != -1:
                    print("\nCall was ended\n")            
                elif lineString.startswith("+CLCC:"):
                    callIncoming = isCallIncoming(lineString)

                          
        #Handset lifted and no call incoming. Prepare to read from rotary dial.    
        if(cradleSwitch.isHandsetLifted() and not callIncoming):
            
            print("Handset lifted, no call incoming, ready to dial out")
            
            #Play the dial tone
            pc.send(atCommandPlayDialTone.encode())
            
            #Create rotary dial thread and prepare to read in a telephone number
            rotaryDial = RotaryDial() 
            dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(True,endListeninglock,diallingStartedLock,3,))
            dialThread.start()
            
            endDialTonecommandSent = False
            
            #Then wait until dialling complete/timed-out or handset returned to cradle
            while(dialThread.is_alive() and cradleSwitch.isHandsetLifted()):
                
                time.sleep(0.1)
                
                diallingStartedLock.acquire()  
                if(rotaryDial.isDialingStarted() and not endDialTonecommandSent):
                    pc.send(atCommandStopAudio.encode())
                    endDialTonecommandSent = True
                diallingStartedLock.release()               
        
            endListeninglock.acquire()
            rotaryDial.endListening()
            endListeninglock.release()
            
            dialThread.join()
        
            #If a number was dialled, do something with it.
            #Else play a message telling user to hang-up and re-dial
            if(rotaryDial.getPhoneNumber()):
                
                phoneNumber = rotaryDial.getPhoneNumber()
                initiateCallCommand = atCommandDialOut.format(phoneNumber)
                print("Phone Number dialled: " + phoneNumber)
                
                #Initiate an outgoing all here
                pc.send(initiateCallCommand.encode())
                
                #Create another dial thread in case presented with an in-call menu
                rotaryDial = RotaryDial() 
                dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(False,endListeninglock,diallingStartedLock,0.25,))
                dialThread.start()
                
                while(cradleSwitch.isHandsetLifted()):
                    
                    time.sleep(0.1)
                    
                    data = pc.receive()
                    if data:
                        for lineBytes in data:
                            lineString = lineBytes.decode("utf-8")
                            print(lineString)        
                            if lineString.startswith("+CLCC:"):
                                callIncoming = isCallIncoming(lineString)
                    
                    #If a number was dialed, send this via AT command and spawn new dial thread
                    if(not dialThread.is_alive() and rotaryDial.getPhoneNumber()):
                        dtmfChar = rotaryDial.getPhoneNumber()
                        
                        print("In-call Number dialled: " + dtmfChar)
                        
                        pc.send(atCommmandSendDTMF.format(dtmfChar).encode())
                        
                        rotaryDial = RotaryDial() 
                        dialThread = threading.Thread(target=rotaryDial.dialHandler, args=(False,endListeninglock,diallingStartedLock,0.25,))
                        dialThread.start()
                        
            elif cradleSwitch.isHandsetLifted() and rotaryDial.isDiallingTimedOut():             
                #If Dialling not started and handset still off-hook play an error message
                print("Playing off-hook message until handset replaced")
                pc.send(atCommandPlayOffHook.encode())
                        
            endListeninglock.acquire()
            rotaryDial.endListening()
            endListeninglock.release()
            
            dialThread.join()
            
            while cradleSwitch.isHandsetLifted():
                time.sleep(0.1)
            
            pc.send(atCommandStopAudio.encode())
            pc.send(atCommandHangUp.encode())
            
            print("Handset replaced after call")
             
        #Handset not lifted and call incoming. Ring the bells until handset lifted or call is dropped.    
        elif(not cradleSwitch.isHandsetLifted() and callIncoming):
            
            print("Call incoming, line is free (Handset Not Lifted)")
            
            #Ring bell for as long as there is an incoming call and handset not lifted
            pygame.mixer.music.load("./Docs/Sound Effects/british_phone_bell.mp3")
            pygame.mixer.music.play(-1)
    
            while not cradleSwitch.isHandsetLifted() and callIncoming:
                time.sleep(0.1)
                
                data = pc.receive()
    
                if data:
                    for lineBytes in data:
                        lineString = lineBytes.decode("utf-8")
                        print(lineString)        
                        if lineString.startswith("+CLCC:"):
                            callIncoming = isCallIncoming(lineString)
            
            pygame.mixer.music.stop()
                                                          
            pc.send(atCommandAnswerCall.encode())                                             
            
            print("Incoming call, waiting for handset to be replaced")
            
            while cradleSwitch.isHandsetLifted():
                time.sleep(0.1)
                data = pc.receive()
                if data:
                    for lineBytes in data:
                        lineString = lineBytes.decode("utf-8")
                        print(lineString)        
                        if lineString.startswith("+CLCC:"):
                            callIncoming = isCallIncoming(lineString)
                            
            pc.send(atCommandHangUp.encode())
            callIncoming = False
            print("Handset replaced after call")
                                           
      
except KeyboardInterrupt:
    print("Cleaning up pins")
    pc.send(atCommandStopAudio.encode())
    pc.send(atCommandHangUp.encode())
    GPIO.cleanup()
except Exception as e:
    print(e)
    print("Cleaning up pins")
    pc.send(atCommandStopAudio.encode())
    pc.send(atCommandHangUp.encode())
    GPIO.cleanup()
finally:
    print("Cleaning up pins")
    pc.send(atCommandStopAudio.encode())
    pc.send(atCommandHangUp.encode())
    GPIO.cleanup()