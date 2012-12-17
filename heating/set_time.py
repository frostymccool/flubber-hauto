#
# Neil Trimboy 2011
#
# Sets current time/date to all controllers
#
# Despite Heatmiser V3 protocol document stating that current day/h/m/s is on 4 separate addresses [43,46]
# Tests showed that it was not possible to write to individual value anf that all 4 values must be written in a single command
import serial
from struct import pack
import time
import sys
import os

from stats_defn import *
from hm_constants import *
from hm_utils import *
#from comms_settings import *

# CODE STARTS HERE

problem = 0

#ferr = open('errorlog2.txt', 'a')
#sys.stderr = open('errorlog.txt', 'a') # Redirect stderr

# Generate a RFC2822 format date
# This works with both Excel and Timeline
localtime = time.asctime( time.localtime(time.time()))
polltime  = time.time()
polltimet = time.localtime(polltime)
localtime = time.strftime("%d %b %Y %H:%M:%S +0000", polltimet)
localday  = time.strftime("%w", polltimet)

serport = serial.Serial()
serport.port = COM_PORT
serport.baudrate = COM_BAUD
serport.bytesize = COM_SIZE
serport.parity = COM_PARITY
serport.stopbits = COM_STOP
serport.timeout = COM_TIMEOUT
try:
    serport.open()
except serial.SerialException, e:
        s= "%s : Could not open serial port %s: %s\n" % (localtime, serport.portstr, e)
        sys.stderr.write(s)
        problem += 1
        #mail(you, "Heatmiser TimeSet Error ", "Could not open serial port", "errorlog.txt")
        sys.exit(1)

print "%s port configuration is %s" % (serport.name, serport.isOpen())
print "%s baud, %s bit, %s parity, with %s stopbits, timeout %s seconds" % (serport.baudrate, serport.bytesize, serport.parity, serport.stopbits, serport.timeout)

good = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # TODO one bigger than size required YUK
#bad =  [0,0,0,0,0,0,0,0,0,0,0,0,0]

def setTime(controller, serport):
    global good
    
    loop = controller[SL_ADDR] #BUG assumes statlist is addresses are 1...n, with no gaps or random

    print "Testing control %2d in %s *****************************" % (loop, controller[SL_LONG_NAME])

    try:
        if hmUpdateTime(controller, serport)==0:
            good[loop] = 1  #once set correctly flag it, such that we don't call again during retry loop
    except:
        print "Error setting time for %s at address %2d, moving on" % (controller[SL_LONG_NAME], loop)
 
	time.sleep(2) # sleep for 2 seconds before next controller

# create a 5 time retry loop
for retry in range(5):
    # CYCLE THROUGH ALL CONTROLLERS
    for controller in StatList:
        if good[controller[SL_ADDR]]==0:
            setTime(controller,serport)

    #END OF CYCLE THROUGH CONTROLLERS

serport.close() # close port
print "Port is now %s" % serport.isOpen()
#ferr.close()

#if (problem > 0):
	#mail(you, "Heatmiser TimeSet Error ", "A Problem has occurred", "errorlog.txt")
