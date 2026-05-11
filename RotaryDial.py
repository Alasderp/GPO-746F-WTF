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
        self.DiallingTimedOut = False
        self.TimeLastNumberDialled = 0
        self.EndListening = False
        
    def isDialingStarted(self):
        return self.DiallingStarted
    
    def isDialingFinished(self):
        return self.DiallingFinished
    
    def isDiallingTimedOut(self):
        return self.DiallingTimedOut
    
    def getPhoneNumber(self):
        return self.phoneNumber
    
    def endListening(self):
        self.EndListening = True


    '''
    When the rotary dial is pulled back, the circuit is complete

    The dial is then released and winds down. A switch will open and close (Connected to GPIO 18 via Orange wire) during this time.
    Count how many times the circuit is interrupted on the orange wire to calculate the number dialled

    On the Pink wire, the circuit remains complete from when the dial is wound back to when it stops rotating.
    This is used to determine when a digit has started and finished dialling.

    In this code the Pink wire is not used, and the time from last digit dialled is instead counted
    '''
    def dialHandler(self, timeout, endListeninglock, diallingStartedLock):
        timeHandsetLifted = time.time()
        while True:
            time.sleep(0.001)
            
            endListeninglock.acquire()
            if self.EndListening:
                print("Rotary Dial End Listening flag set to true, thread self-destructing")
                endListeninglock.release()
                break
            endListeninglock.release()
                                        
            #If no activity after 15 seconds break out of loop
            diallingStartedLock.acquire()
            if(timeout and not self.DiallingStarted and (time.time() - timeHandsetLifted) > 15):
                print("No activity on dial, thread self-destructing")
                self.DiallingTimedOut = True
                diallingStartedLock.release()
                break
            diallingStartedLock.release()
            
            #If dialling has started, and 1/4 of a second has elapsed
            #Assume a single digit has been dialled
            if(self.DiallingNumber and (time.time() - self.TimeLastNumberDialled) > 0.25):
                
                if(self.pulses == 11):
                    self.phoneNumber = self.phoneNumber + '0'
                else:
                    self.phoneNumber = self.phoneNumber + str(self.pulses - 1)
                    
                #print("Phone Number: " + self.phoneNumber)
                                
                #Reset the state, ready for next number to be dialled
                self.DiallingNumber = False
                self.pulses = 0
            
            #If time since last number dialled > 3 secs assume the complete number is dialled
            if(self.phoneNumber and (time.time() - self.TimeLastNumberDialled) > 3):
                self.DiallingFinished = True
                break
            
            if GPIO.event_detected(18):
                
                diallingStartedLock.acquire()
                self.DiallingStarted = True
                diallingStartedLock.release()
                
                current = GPIO.input(18)           

                if(self.last != current):                      
                    if(current != 0):
                        self.TimeLastNumberDialled = time.time()
                        self.DiallingNumber = True
                        self.pulses = self.pulses + 1
                        #time.sleep(0.1)

                    self.last = GPIO.input(18)                 
