#!/usr/bin/env python3

# Orange wire connected to GPIO18
# Brown wire to GND

import RPi.GPIO as GPIO
import time

class RotaryDial:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(18, GPIO.BOTH)

        self.pulses = 0
        self.last = 1
        self.phoneNumber = ''
        self.DiallingNumber = False
        self.DiallingStarted = False
        self.DiallingFinished = False
        self.TimeLastNumberDialled = 0
        
    def isDialingFinished(self):
        return self.DiallingFinished
        
    def isDialingStarted(self):
        return self.DiallingStarted
    
    def getPhoneNumber(self):
        return self.phoneNumber

    '''
    When the rotary dial is pulled back, the circuit is complete

    The dial is then released and winds down. A switch will open and close (Connected to GPIO 18 via Orange wire) during this time.
    Count how many times the circuit is interrupted on the orange wire to calculate the number dialled

    On the Pink wire, the circuit remains complete from when the dial is wound back to when it stops rotating.
    This is used to determine when a digit has started and finished dialling.

    In this code the Pink wire is not used, and the time from last digit dialled is instead counted
    '''
    def dialHandler(self):
        timeHandsetLifted = time.time()
        while True:
            
            #If no activity after 15 seconds break out of loop
            if(not self.DiallingStarted and (time.time() - timeHandsetLifted) > 15):
                print("No activity on dial, thread self-destructing")
                break
            
            #If dialling has started, and 1/4 of a second has elapsed
            #Assume a single digit has been dialled
            if(self.DiallingNumber and (time.time() - self.TimeLastNumberDialled) > 0.25):
                
                if(self.pulses == 11):
                    self.phoneNumber = self.phoneNumber + '0'
                else:
                    self.phoneNumber = self.phoneNumber + str(self.pulses - 1)
                                
                #Reset the state, ready for next number to be dialled
                self.DiallingNumber = False
                self.pulses = 0
            
            #If time since last number dialled > 5 secs assume the complete number is dialled
            if(self.phoneNumber and (time.time() - self.TimeLastNumberDialled) > 5):
                self.DiallingFinished = True
                break
            
            if GPIO.event_detected(18):
                
                self.DiallingStarted = True
                
                current = GPIO.input(18)           

                if(self.last != current):                      
                    if(current != 0):
                        self.TimeLastNumberDialled = time.time()
                        self.DiallingNumber = True
                        self.pulses = self.pulses + 1
                        time.sleep(0.1)

                    self.last = GPIO.input(18)               
