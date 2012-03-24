#
# Ian Shaw 2012
#
# Based on code set from Neil Trimboy (http://code.google.com/p/heatmiser-monitor-control)
#
# Functions to support heatmiser setup, these functions will be used by the XAP handler

# hm_lock(on/off,nodes=StatList)
# hm_setTemp(temp,nodes=StatList)
# hm_setTemp(temp,nodeName<string>))
# hm_getTemp(nodes)
# hm_setTime(datetime=0,nodes=StatList) # [yyyy,mm,dd,hh,mm,ss] 
#               / 0 to use system date/time generally called 
#               on server startup or when calendar events for 
#               twice yearly clock changes.
# hm_setHoldTime(time,temp=0,nodes=StatList) 
#
import serial
from struct import pack
import time
import sys
import os

from stats_defn import *
from hm_constants import *
from hm_utils import *

# hm_lock(state, node=StatList)
# inputs:   state: string 'lock'/'unlock'
#           nodes: will be the array of the tstats that need operating on
# return true for good status return
def hm_lock(state, nodes, serport) :
    err=0
    if (state=='lock') :
        state=KEY_LOCK_LOCK
    else :
        state = KEY_LOCK_UKLOCK

    for node in nodes :
        err += hmKeyLock(node, state, serport)

    return err

# hm_setTemp(temp, nodes)
# inputs:   temp: temperature value to set
#           nodes: will be the array of the tstats that need operating on
# return true for good status return
def hm_setTemp(temp, nodes, serport) :
    err=0

    for node in nodes :
        err += hm_SetNodeTemp(temp, node, serport)
    
    return err

# hm_SetNodeTemp(temp, node, serport)
# set individual node temperature
# node is the array element from the StatList structure
SET_TEMP_CMD=18
def hm_SetNodeTemp(temperature, node, serport) :
    """hm_SetNodeTemp(temp, node, serport): set individual node temperature"""
    err=0

    payload = [temperature]

    msg = hmFormMsgCRC(node[0], node[SL_CONTR_TYPE], MY_MASTER_ADDR, FUNC_WRITE, SET_TEMP_CMD, payload)

    print msg
    string = ''.join(map(chr,msg))

    err = hm_sendwritecmd(node[0], string, serport)

    if (err==1) :
        print "Failure to SetNodeTemp to %d on tstat address %d" % (temperature,node[0])

    return err

# hm_GetNodeTemp(node, serport)
# gets and returns individual node temperature
# node is the array element from the StatList structure
GET_TEMP_CMD=38
def hm_GetNodeTemp(node, serport) :
    """hm_GetNodeTemp(node, serport) : get node temp and return it"""
    err=0

    #payload = []

    # msg = hmFormMsgCRC(node[0], node[SL_CONTR_TYPE], MY_MASTER_ADDR, FUNC_WRITE, SET_TEMP_CMD, payload)

    #print msg
    #string = ''.join(map(chr,msg))

    # result = hm_sendreadcmd(node[0], string, serport)

    #temp = result[0]

    if (err==1) :
        print "Failure to GetNodeTemp to %d on tstat address %d" % (temperature,node[0])

    return 22.2

# generic function for sending a write command and validating the response
# nodeAddress is the tstat communication address
# message is the complete payload including crc
def hm_sendwritecmd(nodeAddress,  message, serport, protocol=HMV3_ID) :
    """generic function for sending a write command and validating the response"""
    err=0

    # print serport

    try:
        written = serport.write(message)  # Write the complete message packet
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)	# NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, nodeAddress, FUNC_WRITE, 2, datal) == False):
        err = 1;
        print "OH DEAR BAD RESPONSE"

    return err

# generic function for sending a read command, validating and returning the buffer
def hm_sendreadcmd(nodeAddress,  message, serport, protocol=HMV3_ID) :
    """generic function for sending a write command and validating the response"""
    err=0

# use heating.py as the base to construct the read command

    try:
        written = serport.write(message)  # Write the complete message packet
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)	# NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, nodeAddress, FUNC_WRITE, 2, datal) == False):
        err = 1;
        print "OH DEAR BAD RESPONSE"



    return result
