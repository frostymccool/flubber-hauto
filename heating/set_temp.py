#
# Ian Shaw
#
# Debug script to set temperature on all array t-stats
#

import serial
from struct import pack
import time
import sys
import os

from stats_defn import *
from hm_constants import *
from hm_utils import *
from hm_controlfuncs import *


problem = 0

#sys.stderr = open('errorlog.txt', 'a') # Redirect stderr

serport = serial.Serial()
serport.port     = S_PORT_NAME
serport.baudrate = 4800
serport.bytesize = serial.EIGHTBITS
serport.parity   = serial.PARITY_NONE
serport.stopbits = serial.STOPBITS_ONE
serport.timeout  = 3

try:
    serport.open()
except serial.SerialException, e:
        s= "%s : Could not open serial port %s: %s\n" % (localtime, serport.portstr, e)
        sys.stderr.write(s)
        problem += 1
        #mail(you, "Heatmiser TempSet Error ", "Could not open serial port", "errorlog.txt")
        sys.exit(1)

print "%s port configuration is %s" % (serport.name, serport.isOpen())
print "%s baud, %s bit, %s parity, with %s stopbits, timeout %s seconds" % (serport.baudrate, serport.bytesize, serport.parity, serport.stopbits, serport.timeout)

#good = [0,0,0,0,0,0,0,0,0,0,0,0,0] # TODO one bigger than size required YUK
#bad =  [0,0,0,0,0,0,0,0,0,0,0,0,0]

badresponse = range(12+1) #TODO hardcoded 12 here! YUK

temp = 23

# CYCLE THROUGH ALL CONTROLLERS
for controller in StatList:
	loop = controller[0] #BUG assumes statlist is addresses are 1...n, with no gaps or random
	print
	print "Setting Temperature to %d for address %2d in location %s *****************************" % (temp, loop, controller[2])
	badresponse[loop] = 0
	tstat = controller # pass through the the tstat array in the statlist
	hm_SetNodeTemp(temp, tstat, serport)

	time.sleep(2) # sleep for 2 seconds before next controller

#END OF CYCLE THROUGH CONTROLLERS
print serport

serport.close() # close port
print "Port is now %s" % serport.isOpen()

