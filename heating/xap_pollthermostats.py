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
import syslog

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

readingsTaken=0

syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

def polltstats(xap):
    global readingsTaken
    global temperaturesCurrent
    global temperaturesPrevious
    global badresponse
    
    # iterate through controllers in StatList
    for controller in StatList:
        loop = controller[0] #BUG assumes statlist is addresses are 1...n, with no gaps or random
        badresponse[loop] = 0
        tstat = controller # pass through the the tstat array in the statlist
           
        # 1 - read the t-stat
        try:
            serport.open()

            temperaturesCurrent[loop] = hm_GetNodeTemp(tstat, serport)
            print "\nRead Temperature for address %2d in location %s as %2.1f *****************************" % (loop, controller[SL_LONG_NAME], temperaturesCurrent[loop])
 
            # make sure we close the serial port before moving on
            serport.close()

        except serial.SerialException, e:
            s= "%s : Could not open serial port %s, wait until next time for retry: %s\n" % (localtime, serport.portstr, e)
            sys.stderr.write(s)
        
        except:
            # leave temperaturesCurrent[loop] unaffected, therefore reusing previous value
            print "\nException caught while reading temp for location %s, moving on to next device **********" % (controller[SL_LONG_NAME])
            
        # 2 - do we need to send the xap event
        # check if the new temp read is the same as previous, if same, then move on, no need to send

        # create the xap event
        msg = "input.state\n{\nstate=on\ntext=%2.1f\n}" % temperaturesCurrent[loop]
        #print msg
                   
        # use an exception handler; if the network is down this command will fail
        try:
            if temperaturesCurrent[loop] != temperaturesPrevious[loop]:
                xap.sendInstanceEventMsg( msg, controller[SL_XAP_INSTANCE] )
                temperaturesPrevious[loop] = temperaturesCurrent[loop]
            else:
                # send info message as no state change
                xap.sendInstanceInfoMsg( msg, controller[SL_XAP_INSTANCE] )
        except:
            print "Failed to send xAP, network may be down"
                    
        # 3 - check to service any pending xap events
        # ...............

        time.sleep(1) # sleep for 30 seconds before next controller, while the stat list is small, 30sec periods are quick enough

    readingsTaken+=1
    if readingsTaken % 10:
        syslog.syslog(syslog.LOG_INFO, 'logged:%d stat looops' % readingsTaken)
    
    # wait another 30 seconds before attempting another read
    sleep(30)



def checkHeatingMessage(xap):
    msg = "11"
    nummsg = 0
    while len(msg)>1:
        msg = xap.receive()
        print "Message Length: %d" % len(msg)
        if len(msg)>0:
            print msg
            nummsg+=1
                
        print "Num messages in block: %d" % nummsg

    sleep(10)


syslog.syslog(syslog.LOG_INFO, 'Processing started')

Xap("F4061101","shawpad.rpi.heating").run(polltstats)
#Xap("F4061102","shawpad.rpi.heating").run(checkHeatingMessage)

syslog.syslog(syslog.LOG_ERR, 'Unexpectidely quit')
