#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(24, GPIO.OUT)

GPIO.output(24, 0)

time.sleep(1)

GPIO.output(24, 1)