#!/usr/bin/env python
# Heatmiser Thermostats Polling
# Polls the list of TStats and sends out current temperatures for every stat
# Polling by default once per minute

# code located on http://code.google.com/p/flubber-hah
# reference code for vbusdecode from http://code.google.com/p/heatmiser-control
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

from stats_defn import *
from hm_constants import *
from hm_utils import *
from hm_controlfuncs import *
from xap_handle_heating_requests import *

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
serialReadsGood=0
serialReadsBad=0

# thread
serialmutex=0
xapmutex=0

# debug / logging
readingsTaken=0
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

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

def readStat(tstat):
    global serport
    
    temp = -1
    grabbedMutex=0
    
    # 1 - read the t-stat
    try:
        # first wait to make sure no other thread is using the serial
        obtainMutexSerialAccess(serport)
        grabbedMutex=1
        
        temp = hm_GetNodeTemp(tstat, serport)
        print "\nRead Temperature for address %2d in location %s as %2.1f *****************************" % (tstat[0], tstat[SL_LONG_NAME], temp)
        
    except serial.SerialException, e:
        s= "%s : Could not open serial port %s, wait until next time for retry: %s\n" % (localtime, serport.portstr, e)
        sys.stderr.write(s)
        temp=-1
        
    except:
        # leave temperaturesCurrent[loop] unaffected, therefore reusing previous value
        print "\nException caught while reading temp for location %s, moving on to next device **********" % (tstat[SL_LONG_NAME])
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
    
    # normal operation iterate through controllers in StatList, reading their status
    for controller in StatList:
        print "Starting: %s...." % controller[SL_LONG_NAME]
        
        #before next step, check for any events that need servicing
        servicexAPStack(xap)
        
        loop = controller[0] #BUG assumes statlist is addresses are 1...n, with no gaps or random
        badresponse[loop] = 0
        tstat = controller # pass through the the tstat array in the statlist
        
        # 1 - read the t-stat
        # Only read the t-stat if this thermal element actually has a t-stat
        if tstat[SL_STAT_PRESENT]:
            t=readStat(tstat)
            if t==-1:
                serialReadsBad+=1
                continue #bad read, so no message to send, skip to next in list
  
        serialReadsGood+=1
        temperaturesCurrent[loop]=t

        #before next step, check for any events that need servicing
        servicexAPStack(xap)
   
        # create the xap event
        msg = "input.state\n{\nstate=on\ntext=%2.1f\n}" % temperaturesCurrent[loop]
        #print msg
                   
        # use an exception handler; if the network is down this command will fail
        # make sure to send an event or info, depdending on previous sent message value

        try:
            if temperaturesCurrent[loop] != temperaturesPrevious[loop]:
                xap.sendInstanceEventMsg( msg, controller[SL_XAP_INSTANCE] )
                temperaturesPrevious[loop] = temperaturesCurrent[loop]
                #print("event message")
            else:
                # send info message as no state change
                xap.sendInstanceInfoMsg( msg, controller[SL_XAP_INSTANCE] )
                #print("info messge")
        except:
            print "Failed to send xAP, network may be down"
        
        time.sleep(1) # sleep between elements
            
    readingsTaken+=1
    if readingsTaken % 10:
        syslog.syslog(syslog.LOG_INFO, 'logged:%d stat looops - Good:%d, Bad:%d' % (readingsTaken, serialReadsGood, serialReadsBad))
    
    # wait another 30 seconds before attempting another read
    sleep(15)



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

#while(1):
#    try:
Xap("F4061101","shawpad.rpi.heating").run(heatingHandler)
#Xap("F4061102","shawpad.rpi.heating").run(checkHeatingMessage)

#    except:
#        syslog.syslog(syslog.LOG_ERR, 'Xap Crash')

