#
# Ian Shaw 2012
#
# Based on code set from Neil Trimboy (http://code.google.com/p/heatmiser-monitor-control)
#
# Functions to support heatmiser setup, these functions will be used by the XAP handler

# hm_lock(on/off,node-=all(0))
# hm_settemp(temp,node=all(0))
# hm_gettemp(node=all(0))
# hm_settime(datetime=0,node=all(0)) # [yyyy,mm,dd,hh,mm,ss] 
#               / 0 to use system date/time generally called 
#               on server startup or when calendar events for 
#               twice yearly clock changes.
# hm_setholdtime(time,temp=0,node=all(0)) 
#
import serial
from struct import pack
import time
import sys
import os

from stats_defn import *
from hm_constants import *
from hm_utils import *

# hm_lock(state, node=0)
# inputs:   state: 'lock'/'unlock'
#           node: <num> or 0 for all nodes
# return true for good status return
def hm_lock(state, node=0,serport) :
    err=0
    if (state=='lock') :
        state=KEY_LOCK_LOCK
    else :
        state = KEY_LOCK_UKLOCK

    if (node==0) :
    # loop round all nodes availble in StatList[]
        for x in range(1, len(StatList)/SL_WIDTH) :
            err += hmKeyLock(x, state, serport)
    else :
        err = hmKeyLock(node, state, serport)

    return err

# hm_settemp(temp, node=0)
# inputs:   temp: temperature value to set
#           node: <num> element in StatList array or 0 for all nodes
# return true for good status return
def hm_settemp(temp, node=0, serport) :
    err=0
    
    if (node==0) :
        # loop round all nodes availble in StatList[]
        for x in range(1, len(StatList)/SL_WIDTH) :
            err += hm_SetNodeTemp(temp, node, serport)
    else :
        err = hm_SetNodeTemp(temp, node, serport)
    
    return err

# hm_SetNodeTemp(temp, node, serport)
# set individual node temperature
SET_TEMP_CMD=18
def hm_SetNodeTemp(temp, node, serport)
    err=0

    payload = [temp]

    msg = hmFormMsgCRC(destination, StatList[node][SL_CONTR_TYPE], MY_MASTER_ADDR, FUNC_WRITE, SET_TEMP_CMD, payload)

    print msg
    string = ''.join(map(chr,msg))

    err = hm_sendwritecmd(string, serport)

    if (err=1) :
        print "Failure to SetNodeTemp to %d on node %d" % (temp,node)

    return err

# generic function for sending a write command and validating the response
def hm_sendwritecmd(message, serport)
    err=0

    print serport

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)	# NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, destination, FUNC_WRITE, 2, datal) == False):
        err = 1;
        print "OH DEAR BAD RESPONSE"

    return err

