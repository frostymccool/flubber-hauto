from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

GPIO.output(5, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(18, GPIO.HIGH)

sleep(3)

GPIO.cleanup()
