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

DATAOFFSET = 9

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

    payload = []
    temperature=0

    try:
        payload = hm_sendreadcmd(node[0], serport)
    except e:
        print "Failure to GetNodeTemp() on tstat address %d" % (node)
        err=1

    if (err==0) :
        # parse the payload to extract the current temp
        intairtemphigh = datal[32+ DATAOFFSET]
        intairtemplow  = datal[33+ DATAOFFSET]
        temperature = (intairtemphigh*256 + intairtemplow)/10.0
    else:
        raise "hm_GetNodeTemp failed"


    return temperature

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
def hm_sendreadcmd(nodeAddress, serport, protocol=HMV3_ID) :
    """generic function for sending a read command and validating the response. The entire read block is then returned for parsing"""
    # @todo parse the read block into a structure
    err=0

    start_low = 0
    start_high = 0
    read_length_high = (RW_LENGTH_ALL & 0xff)
    read_length_low = (RW_LENGTH_ALL >> 8) & 0xff
    data = [nodeAddress, 0x0a, MY_MASTER_ADDR, FUNC_READ, start_low, start_high, read_length_low, read_length_high]
    #print data
    crc = crc16()
    data = data + crc.run(data)
    print data
    
    string = ''.join(map(chr,data))

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        sys.stderr.write("Write timeout error: %s\n" % (e))
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
        err += 1
        
    # Now wait for reply
    byteread = serport.read(100)	# NB max return is 75 in 5/2 mode or 159 in 7day mode, this does not yet supt 7 day
    #print "Bytes read %d" % (len(byteread) )
    #TODO checking for length here can be removed
    if (len(byteread)) == 75:
        print  "Correct length reply received"
    else:
        print "Incorrect length reply %s" % (len(byteread))
        s= "%s : Controller %2d : Incorrect length reply : %s\n" % (localtime, nodeAddress, le(byteread))
        sys.stderr.write(s) 
        err += 1		

    # TODO All this should only happen if correct length reply
    #Now try converting it back to array
    datal = []
    datal = datal + (map(ord,byteread))
        
    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, controller[SL_CONTR_TYPE], destination, FUNC_READ, 75, datal) == False):
        err += 1
        
    if (err== 0):
		# Should really only be length 75 or TBD at this point as we shouldnt do this if bad resp
		# @todo define magic number 75 in terms of header and possible payload sizes
		# @todo value in next line of 120 is a wrong guess
		if ((len(byteread)) == 75) or ((len(byteread)) == 120):
            return datal

    raise "Invalid Block Read form sendreadcmd()"
    
