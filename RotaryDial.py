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
        self.RotaryDialInitiated = False
        self.TimeLastNumberDialled = 0
        
    def dialingStarted(self):
        return self.RotaryDialInitiated

    '''
    When the rotary dial is pulled back, the circuit is complete

    The dial is then released and winds down. A switch will open and close (Connected to GPIO 18 via Orange wire) during this time.
    Count how many times the circuit is interrupted on the orange wire to calculate the number dialled

    On the Pink wire, the circuit remains complete from when the dial is wound back to when it stops rotating.
    This is used to determine when a digit has started and finished dialling.

    In this code the Pink wire is not used, and the time from last digit dialled is instead counted
    '''
    def dialHandler(self):
        while True:
            
            #If dialling has started, and half a second has elapsed
            #Assume a single digit has been dialled
            if(DiallingNumber and (time.time() - TimeLastNumberDialled) > 0.5):
                
                if(pulses == 11):
                    phoneNumber = phoneNumber + '0'
                else:
                    phoneNumber = phoneNumber + str(pulses - 1)

                print("Phone Number: " + phoneNumber)
                
                RotaryDialInitiated = True
                
                #Reset the state, ready for next number to be dialled
                DiallingNumber = False
                pulses = 0
            
            #If time since last number dialled > 5 secs assume the complete number is dialled
            if(RotaryDialInitiated and (time.time() - TimeLastNumberDialled) > 5):
                print("Finished Dialling The Number: " + phoneNumber)
                break;
            
            if GPIO.event_detected(18):
                
                current = GPIO.input(18)           

                if(last != current):                      
                    if(current != 0):
                        TimeLastNumberDialled = time.time()
                        DiallingNumber = True
                        pulses = pulses + 1
                        time.sleep(0.1)

                    last = GPIO.input(18)
                    
                    
