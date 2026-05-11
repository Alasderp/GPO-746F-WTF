#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import pygame

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#GPIO 21 set as input, pulled up and connected to T3 terminal of phone
#GND pin connected to T6 terminal of phone
GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_UP)

pygame.mixer.init()
pygame.mixer.music.load("../MiscDocs/Sound Effects/UK_dial_tone.mp3")

def handsetMoved(channel):
    global sound
    if GPIO.input(channel):
        print("Handset is placed on cradle")
        pygame.mixer.music.stop()
    else:
        print("Handset is lifted from cradle")
        pygame.mixer.music.play(-1)
            
        
        
try:

    GPIO.add_event_detect(21, GPIO.BOTH, callback=handsetMoved, bouncetime=200)
        
    message = input("\n\nPress enter to quit\n\n")
    
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

