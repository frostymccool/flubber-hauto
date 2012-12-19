#!/usr/bin/env python
# Heating System handler
# loop manages polling of Heatmiser Thermostats and handle xAP events
# listens for xAP events and event slices in xAP / Thermostat updates

# code located on http://code.google.com/p/flubber-hah
# reference code for heatmiser from http://code.google.com/p/heatmiser-control
# reference code for hah/xap from http://code.google.com/p/livebox-hah/

import sys
import signal
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

from data_types import *
from stats_defn import *
from hm_constants import *
from hm_utils import *
from hm_controlfuncs import *
from xap_handle_heating_requests import *
from fl_support import *

serport = serial.Serial()
serport.port     = S_PORT_NAME
serport.baudrate = 4800
serport.bytesize = serial.EIGHTBITS
serport.parity   = serial.PARITY_NONE
serport.stopbits = serial.STOPBITS_ONE
serport.timeout  = 3

tstats =[]
tstats.append(thermostat(1, "Kit", "Kitchen", HMV3_ID, "kitchen.temp", "F4061102"))

temperaturesCurrent=range(15)
temperaturesPrevious=range(15)
badresponse=range(15)
serialReadsGood=0
serialReadsBad=0

# debug / logging
readingsTaken=0
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

def readStat(tstat, xap):
    global serport
    
    temp = -1
    grabbedMutex=0
    
    # 1 - read the t-stat
    try:
        # first wait to make sure no other thread is using the serial
        obtainMutexSerialAccess(serport)
        grabbedMutex=1
        
        temp = tstat.GetxAPNodeTemp(serport, xap)
        print "\nRead Temperature for address %2d in location %s as %2.1f *****************************" % (tstat.address, tstat.longName, temp)
        
    except serial.SerialException, e:
        s= "%s : Could not open serial port %s, wait until next time for retry: %s\n" % (localtime, serport.portstr, e)
        sys.stderr.write(s)
        temp=-1
        
    except:
        # leave temperaturesCurrent[loop] unaffected, therefore reusing previous value
        print "\nException caught while reading temp for location %s, moving on to next device **********" % (tstat.longName)
        temp=-1
        
    # make sure we close the serial port before moving on but only if we grabbed mutex in the first place
    if grabbedMutex:
        releaseMutexSerialAccess(serport)

    return temp

def heatingHandler(xap):
    global readingsTaken
    global temperaturesCurrent
    global temperaturesPrevious
    global badresponse
    global xapmutex
    global serialReadsGood
    global serialReadsBad
    global tstats
    
    # normal operation iterate through controllers in StatList, reading their status
    for controller in tstats:
        print "Starting: %s...." % controller.longName
        
        #before next step, check for any events that need servicing
        servicexAPStack(xap)
        
        loop = controller.address #BUG assumes statlist is addresses are 1...n, with no gaps or random
        tstat = controller # pass through the the tstat array in the statlist
        
        # 1 - read the t-stat
        # Only read the t-stat if this thermal element actually has a t-stat
        #if tstat[SL_STAT_PRESENT]:
        try:
            readStat(tstat,xap)
        except:
            serialReadsBad+=1
            continue #bad read, so no message to send, skip to next in list
  
        serialReadsGood+=1
 
        #before next step, check for any events that need servicing
        servicexAPStack(xap)
   
        time.sleep(1) # sleep between elements
            
    readingsTaken+=1
    if readingsTaken % 10:
        syslog.syslog(syslog.LOG_INFO, 'logged:%d stat looops - Good:%d, Bad:%d' % (readingsTaken, serialReadsGood, serialReadsBad))
    
    # wait another 30 seconds before attempting another read
    sleep(15)


syslog.syslog(syslog.LOG_INFO, 'Processing started')

#while(1):
#    try:
Xap("F4061101","shawpad.rpi.heating").run(heatingHandler)

#    except:
#        syslog.syslog(syslog.LOG_ERR, 'Xap Crash')

