#!/usr/bin/env python
# Heatmiser Thermostats Polling
# Polls the list of TStats and sends out current temperatures for every stat
# Polling by default once per minute

# code located on http://code.google.com/p/flubber-hah
# reference code for vbusdecode from http://code.google.com/p/heatmiser-control
# reference code for hah/xap from http://code.google.com/p/livebox-hah/

import sys
import serial
sys.path.append('../xap')

from xaplib import Xap
from time import localtime, strftime, sleep
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
temperaturesCurrent=range(15)
temperaturesPrevious=range(15)
badresponse=range(15)


def polltstats(xap):

    # iterate through controllers in StatList
    for controller in StatList:
        loop = controller[0] #BUG assumes statlist is addresses are 1...n, with no gaps or random
        badresponse[loop] = 0
        tstat = controller # pass through the the tstat array in the statlist
           
        # 1 - read the t-stat
        try:
            serport.open()

            temperaturesCurrent[loop] = hm_GetNodeTemp(tstat, serport)
            print "\nRead Temperature for address %2d in location %s as %2.1f *****************************" % (loop, controller[2], temperatures[loop])
 
            # make sure we close the serial port before moving on
            serport.close()

        except serial.SerialException, e:
            s= "%s : Could not open serial port %s, wait until next time for retry: %s\n" % (localtime, serport.portstr, e)
            sys.stderr.write(s)
        
        except:
            # leave temperatures[loop] unaffected, therefore reusing previous value
            print "\nException caught while reading temp for location %s, moving on to next device **********" % (controller[2])
            
        try:
            # 2 - do we need to send the xap event
            # check if the new temp read is the same as previous, if same, then move on, no need to send
            if temperaturesCurrent[loop] != temperaturesPrevious[loop]:
                # send the xap event
                msg = "input.state\n{\nstate=on\ntext="
                msg += "%2.1f\n" % temperatures[1]
                msg += "}"
                print msg
                   
                # use an exception handler; if the network is down this command will fail
                try:
                    xap.sendEventMsg( msg )
                except:
                    print "Failed to send xAP, network may be down"
            else:
                temperaturesPrevious[loop] = temperaturesCurrent[loop]
        except:
            print "Exception caught"
                    
        # 3 - check to service any pending xap events
        # ...............

        time.sleep(1) # sleep for 30 seconds before next controller, while the stat list is small, 30sec periods are quick enough
     
    # wait another 45 seconds before attempting another read
    sleep(45)

Xap("F4061101","shawpad.rpi1.heating:kitchentop.temp").run(polltstats)

