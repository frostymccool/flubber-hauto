#
# Neil Trimboy 2011
# Assume Pyhton 2.7.x
#
import serial
from struct import pack
import time
import sys
import os
import shutil
from datetime import datetime

# Import our own stuff
from stats_defn import *
from hm_constants import *


# Believe this is known as CCITT (0xFFFF)
# This is the CRC function converted directly from the Heatmiser C code
# provided in their API
class crc16:
    LookupHigh = [
    0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70,
    0x81, 0x91, 0xa1, 0xb1, 0xc1, 0xd1, 0xe1, 0xf1
    ]
    LookupLow = [
    0x00, 0x21, 0x42, 0x63, 0x84, 0xa5, 0xc6, 0xe7,
    0x08, 0x29, 0x4a, 0x6b, 0x8c, 0xad, 0xce, 0xef
    ]
    def __init__(self):
        self.high = BYTEMASK
        self.low = BYTEMASK

    def Update4Bits(self, val):
        # Step one, extract the Most significant 4 bits of the CRC register
        #print "val is %d" % (val)
        t = self.high>>4
        #print "t is %d" % (t)

        # XOR in the Message Data into the extracted bits
        t = t^val
        #print "t is %d" % (t)

        # Shift the CRC Register left 4 bits
        self.high = (self.high << 4)|(self.low>>4)
        self.high = self.high & BYTEMASK    # force char
        self.low = self.low <<4
        self.low = self.low & BYTEMASK  # force char

        # Do the table lookups and XOR the result into the CRC tables
        #print "t for lookup is %d" % (t)
        self.high = self.high ^ self.LookupHigh[t]
        self.high = self.high & BYTEMASK    # force char
        self.low  = self.low  ^ self.LookupLow[t]
        self.low = self.low & BYTEMASK  # force char
        #print "high is %d Low is %d" % (self.high, self.low)

    def CRC16_Update(self, val):
        self.Update4Bits(val>>4) # High nibble first
        self.Update4Bits(val & 0x0f) # Low nibble

    def run(self, message):
        """Calculates a CRC"""
        for c in message:
            #print c
            self.CRC16_Update(c)
        #print "CRC is Low %d High  %d" % (self.low, self.high)
        return [self.low, self.high]

# TODO is this next comment a dead comment?
# Always read whole DCB
# TODO check master address is in legal range
def hmFormMsg(destination, protocol, source, function, start, payload) :
  """Forms a message payload, excluding CRC"""
  if protocol == HMV3_ID:
    start_low = (start & BYTEMASK)
    start_high = (start >> 8) & BYTEMASK
    if function == FUNC_READ:
      payloadLength = 0
      length_low = (RW_LENGTH_ALL & BYTEMASK)
      length_high = (RW_LENGTH_ALL >> 8) & BYTEMASK
    else:
      payloadLength = len(payload)
      length_low = (payloadLength & BYTEMASK)
      length_high = (payloadLength >> 8) & BYTEMASK
    msg = [destination, 10+payloadLength, source, function, start_low, start_high, length_low, length_high]
    if function == FUNC_WRITE:
      msg = msg + payload
    return msg
  else:
    assert 0, "Un-supported protocol found %s" % protocol

def hmFormMsgCRC(destination, protocol, source, function, start, payload) :
  """Forms a message payload, including CRC"""
  data = hmFormMsg(destination, protocol, source, function, start, payload)
  crc = crc16()
  data = data + crc.run(data)
  return data

# expectedLength only used for read msgs as always 7 for write
def hmVerifyMsgCRCOK(destination, protocol, source, expectedFunction, expectedLength, datal) :
  """Verifies message appears legal"""
  localtime = "<UNKNOWN TIME>" # TODO
  loop = 2 # TODO
  badresponse = 0
  print datal
  if protocol == HMV3_ID:
    checksum = datal[len(datal)-2:]
    rxmsg = datal[:len(datal)-2]
    # print checksum
    print rxmsg
    crc = crc16() # Initialises the CRC
    expectedchecksum = crc.run(rxmsg)
    if expectedchecksum == checksum:
      print "CRC is correct"
    else:
      print "CRC is INCORRECT"
      s = "%s : Controller %s : Incorrect CRC: %s %s \n" % (localtime, loop, datal, expectedchecksum)
      sys.stderr.write(s)
      badresponse += 1

    # Check the  response
    dest_addr = datal[0]
    frame_len_l = datal[1]
    frame_len_h = datal[2]
    frame_len = (frame_len_h << 8) | frame_len_l
    source_addr = datal[3]
    func_code = datal[4]



    if (dest_addr != 129 and dest_addr != 160):
      print "dest_addr is ILLEGAL"
      s = "%s : Controller %s : Illegal Dest Addr: %s\n" % (localtime, loop, dest_addr)
      sys.stderr.write(s)
      badresponse += 1

    if (dest_addr != destination):
      print "dest_addr is INCORRECT"
      s = "%s : Controller %s : Incorrect Dest Addr: %s\n" % (localtime, loop, dest_addr)
      sys.stderr.write(s)
      badresponse += 1

    if (source_addr < 1 or source_addr > 32):
      print "source_addr is ILLEGAL"
      s = "%s : Controller %s : Illegal Src Addr: %s\n" % (localtime, loop, source_addr)
      sys.stderr.write(s)
      badresponse += 1

    if (source_addr != source):
      print "source addr is INCORRECT"
      s = "%s : Controller %s : Incorrect Src Addr: %s\n" % (localtime, loop, source_addr)
      sys.stderr.write(s)
      badresponse += 1

    if (func_code != FUNC_WRITE and func_code != FUNC_READ):
      print "Func Code is UNKNWON"
      s = "%s : Controller %s : Unknown Func Code: %s\n" % (localtime, loop, func_code)
      sys.stderr.write(s)
      badresponse += 1

    if (func_code != expectedFunction):
      print "Func Code is UNEXPECTED"
      s = "%s : Controller %s : Unexpected Func Code: %s\n" % (localtime, loop, func_code)
      sys.stderr.write(s)
      badresponse += 1

    if (func_code == FUNC_WRITE and frame_len != 7):
      # Reply to Write is always 7 long
      print "response length is INCORRECT"
      s = "%s : Controller %s : Incorrect length: %s\n" % (localtime, loop, frame_len)
      sys.stderr.write(s)
      badresponse += 1

    if (len(datal) != frame_len):
      print "response length MISMATCHES header"
      s = "%s : Controller %s : Mismatch length: %s %s\n" % (localtime, loop, len(datal), frame_len)
      sys.stderr.write(s)
      badresponse += 1

    if (func_code == FUNC_READ and expectedLength !=len(datal) ):
      # Read response length is wrong
      print "response length not EXPECTED value"
      s = "%s : Controller %s : Incorrect length: %s\n" % (localtime, loop, frame_len)
      sys.stderr.write(s)
      badresponse += 1

    if (badresponse == 0):
      return True
    else:
      return False

  else:
    assert 0, "Un-supported protocol found %s" % protocol

def hmKeyLock_On(controller, serport) :
  hmKeyLock(controller, KEY_LOCK_LOCK, serport)

def hmKeyLock_Off(controller, serport) :
  hmKeyLock(controller, KEY_LOCK_UNLOCK, serport)

def hmKeyLock(controller, state, serport) :
    """bla bla"""
    protocol = controller[SL_CONTR_TYPE]
    if protocol == HMV3_ID:
        payload = [state]
        msg = hmFormMsgCRC(controller[SL_ADDR], protocol, MY_MASTER_ADDR, FUNC_WRITE, KEY_LOCK_ADDR, payload)
    else:
        "Un-supported protocol found %s" % protocol
        assert 0, "Un-supported protocol found %s" % protocol
        # TODO return error/exception

    print msg
    string = ''.join(map(chr,msg))

    #TODO Need a send msg method

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)    # NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, controller[SL_ADDR], FUNC_WRITE, DONT_CARE_LENGTH, datal) == False):
        print "OH DEAR BAD RESPONSE"
    return 1


def hmSetHolEnd(controller, enddatetime, serport) :
    """bla bla"""
    nowdatetime = datetime.now()
    print nowdatetime
    if enddatetime < nowdatetime:
        print "oh dear" # TODO
    duration = enddatetime - nowdatetime
    days = duration.days
    seconds = duration.seconds
    hours = seconds/(60*60)
    totalhours = days*24 + hours + 1
    print "Setting holiday to end in %d days %d hours or %d total_hours on %s, it is now %s" % (days, hours, totalhours, enddatetime, nowdatetime)
    hmSetHolHours(controller, totalhours, serport)


def hmSetHolHours(controller, hours, serport) :
    """bla bla"""
    protocol = controller[SL_CONTR_TYPE]
    if protocol == HMV3_ID:
        hours_lo = (hours & BYTEMASK)
        hours_hi = (hours >> 8) & BYTEMASK
        payload = [hours_lo, hours_hi]
        msg = hmFormMsgCRC(controller[SL_ADDR], protocol, MY_MASTER_ADDR, FUNC_WRITE, HOL_HOURS_LO_ADDR, payload)
    else:
        "Un-supported protocol found %s" % protocol
        assert 0, "Un-supported protocol found %s" % protocol
        # TODO return error/exception

    print msg
    string = ''.join(map(chr,msg))

    #TODO Need a send msg method

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        # TODO local time not defined?
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)    # NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, controller[SL_ADDR], FUNC_WRITE, DONT_CARE_LENGTH, datal) == False):
        print "OH DEAR BAD RESPONSE"
    return 1

def hmUpdateTime(controller, serport) :
    """bla bla"""
    protocol = controller[SL_CONTR_TYPE]
    if protocol == HMV3_ID:
        msgtime = time.time()
        msgtimet = time.localtime(msgtime)
        day  = int(time.strftime("%w", msgtimet))
        if (day == 0):
            day = 7		# Convert python day format to Heatmiser format
        hour = int(time.strftime("%H", msgtimet))
        mins = int(time.strftime("%M", msgtimet))
        secs = int(time.strftime("%S", msgtimet))
        if (secs == 61):
            secs = 60 # Need to do this as pyhton seconds can be  [0,61]
        print "%d %d:%d:%d" % (day, hour, mins, secs)
        payload = [day, hour, mins, secs]
 
        msg = hmFormMsgCRC(controller[SL_ADDR], protocol, MY_MASTER_ADDR, FUNC_WRITE, CUR_TIME_ADDR, payload)
    else:
        "Un-supported protocol found %s" % protocol
        assert 0, "Un-supported protocol found %s" % protocol
        # TODO return error/exception

    #print msg
    # http://stackoverflow.com/questions/180606/how-do-i-convert-a-list-of-ascii-values-to-a-string-in-python
    string = ''.join(map(chr,msg))

    #TODO Need a send msg method

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)    # NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, controller[SL_ADDR], FUNC_WRITE, DONT_CARE_LENGTH, datal) == False):
        print "OH DEAR BAD RESPONSE"
        return 1
    return 0

def hmSetTemp(controller, temp, serport) :
    """bla bla"""
    protocol = controller[SL_CONTR_TYPE] 
    if protocol == HMV3_ID:
        payload = [temp]
        msg = hmFormMsgCRC(controller[SL_ADDR], protocol, MY_MASTER_ADDR, FUNC_WRITE, SET_TEMP_ADDR, payload)
    else:
        "Un-supported protocol found %s" % protocol
        assert 0, "Un-supported protocol found %s" % protocol
        # TODO return error/exception

    print msg
    string = ''.join(map(chr,msg))

    #TODO Need a send msg method

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)    # NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, controller[SL_ADDR], FUNC_WRITE, DONT_CARE_LENGTH, datal) == False):
        print "OH DEAR BAD RESPONSE"
    return 1
    
def hmHoldTemp(controller, temp, minutes, serport) :
    """bla bla"""
    # @todo reject if number too big
    hmSetTemp(controller, temp, serport)
    time.sleep(2) # sleep for 2 seconds before next controller
    protocol = controller[SL_CONTR_TYPE]
    if protocol == HMV3_ID:
        minutes_lo = (minutes & BYTEMASK)
        minutes_hi = (minutes >> 8) & BYTEMASK
        payload = [minutes_lo, minutes_hi]
        # TODO address - is this different for a read? think so , so how do constant
        msg = hmFormMsgCRC(controller[SL_ADDR], protocol, MY_MASTER_ADDR, FUNC_WRITE, 32, payload)
    else:
        "Un-supported protocol found %s" % protocol
        assert 0, "Un-supported protocol found %s" % protocol
        # TODO return error/exception

    print msg
    string = ''.join(map(chr,msg))

    #TODO Need a send msg method

    try:
        written = serport.write(string)  # Write a string
    except serial.SerialTimeoutException, e:
        s= "%s : Write timeout error: %s\n" % (localtime, e)
        sys.stderr.write(s)
    # Now wait for reply
    byteread = serport.read(100)    # NB max return is 75 in 5/2 mode or 159 in 7day mode
    datal = []
    datal = datal + (map(ord,byteread))

    if (hmVerifyMsgCRCOK(MY_MASTER_ADDR, protocol, controller[SL_ADDR], FUNC_WRITE, DONT_CARE_LENGTH, datal) == False):
        print "OH DEAR BAD RESPONSE"
    return 1