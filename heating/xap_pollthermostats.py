#!/usr/bin/env python
# Heatmiser Thermostats Polling
# Polls the list of TStats and sends out current temperatures for every stat
# Polling by default once per minute

# code located on http://code.google.com/p/flubber-hah
# reference code for vbusdecode from http://code.google.com/p/heatmiser-control
# reference code for hah/xap from http://code.google.com/p/livebox-hah/

import sys
sys.path.append('../xap')

from xaplib import Xap
from time import localtime, strftime, sleep
import serial
import binascii
import subprocess 
import re
from struct import pack
import os

from stats_defn import *
from hm_constants import *
from hm_utils import *
from hm_controlfuncs import *

serport = serial.Serial()
serport.port     = S_PORT_NAME
serport.baudrate = 4800
serport.bytesize = serial.EIGHTBITS
serport.parity   = serial.PARITY_NONE
serport.stopbits = serial.STOPBITS_ONE
serport.timeout  = 3

# TODO: remove hardcoded size
temperatures=range(15)

def polltstats(xap):

    try:
       serport.open()

       # iterate through controllers in StatList
       for controller in StatList:
           loop = controller[0] #BUG assumes statlist is addresses are 1...n, with no gaps or random
	   print
	   badresponse[loop] = 0
	   tstat = controller # pass through the the tstat array in the statlist
	   temperatures[loop] = hm_ReadNodeTemp(temp, tstat, serport)
	   print "Read Temperature for address %2d in location %s as %2.2f *****************************" % (temp, loop, controller[2], temperatures[loop])

	   time.sleep(2) # sleep for 2 seconds before next controller

       print "Sending xAP.."

       # compile message for all stat temps, create message on a tstat name basis
       # TODO: review, do I send one packet per tstat or combined packet with all readings?
       msg = "data\n{\n" 
       for controller in StatList :
           msg += "%s=%2.2f\n" % (controller[SL_SHRT_NAME], temperatures[controller[SL_ADDR]])

       msg += "}"

       serport.close()

       # use an exception handler; if the network is down this command will fail
       try:
          #xap.sendHeatBeat(180)
          xap.sendSolarEventMsg( msg )
       except:
          print "Failed to send xAP, network may be down"
      
    except serial.SerialException, e:
        s= "%s : Could not open serial port %s, wait until next time for retry: %s\n" % (localtime, serport.portstr, e)
        sys.stderr.write(s)  

    # wait another 45 seconds before attempting another read
    sleep(45)

Xap("FF000F00","shawpad.ujog.tstats").run(polltstats)

