
import sys
import signal
import serial

from time import localtime, strftime, sleep
import binascii
import subprocess


# thread mutexs
serialmutex=0
xapmutex=0

class TimeoutException(Exception):
    pass

# use the mutex variable to control access to the serial portdef obtainMutexSerialAccess():
def obtainMutexSerialAccess(serport):
    global serialmutex
    
    def timeout_handler(signum, frame):
        print "Timeout exeption while waiting for serial mutex"
        raise TimeoutException()
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30) # allow 30 secs for the other process to complete before timing out
    
    while (serialmutex==1):
        # do nothing other than checking for timeout
        x=0
    
    # mutext now been released, so grab it and open the serial port
    serialmutex=1
    serport.open()

def releaseMutexSerialAccess(serport):
    global serialmutex
    serport.close()
    serialmutex=0

