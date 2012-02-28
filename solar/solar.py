#!/usr/bin/env python
# Water Solar Collector Readings Logger
# Grabs information from the vbus console and post xap to the Network
 
# code located on http://code.google.com/p/my-jog-home
# reference code for vbusdecode from http://code.google.com/p/vbusdecode/
# reference code for hah/xap from http://code.google.com/p/livebox-hah/

from xaplib import Xap
from time import localtime, strftime, sleep
import serial
import binascii
import subprocess 
import re

# sequence / process
# uses vbusdecode compiled c from vbusdecode on google code projects (thanks)
# check for new solar reading every 45 seconds
# if values have changed from previous, post a new xapEvent
# if no events have been posted for 3 new readings then post an xapInfo packet
# need to generate heatbeat events - need to work out how often to send them


# need to keep some old values, so as not to dump event when no change in values
pCol=0
pBottom=0
pTop=0
pPump=0

def solar(xap):
    s = serial.Serial("/dev/ttyUSB0")

    # test - read 100 bytes from serial port and print out (non formatted, thus garbled
    line = s.read(100)

    # convert to ascii 
    # print binascii.hexlify(line)

    # close the serial port as it won't be used for 5 secs
    s.close()

    # decode the line, at the moment, system calling the vbusdecode binary, 
    # should really put the decode in python
    vb = subprocess.Popen(["./vbusdecode", "0,15,0.1", "2,15,0.1", "4,15,0.1", "6,15,0.1", "8,7,1", "9,7,1"],  stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
    result = vb.communicate(line)[0]

    # make sure only one frame is present from decode
    #result = result[:26]
    #print result

    # split the results into their core parts
    if len(result)>20 :
       col, bottom, top, sp4, pump, sp1 = re.split('\ +',result,5)

       col=float(col)
       bottom=float(bottom)
       top=float(top)
       if pump==100 :
         pump="On"
       else :
         pump="Off"

       # adjust collector for -ve
       if col>600:
         col=(col-6550.6)*-1

       

       print "Captured reading: ",
       print "col=",col, " bot=",bottom, " top=",top, " pump=",pump,

       print "Sending xAP.."

       msg = "data\n{\ncoltemp=%.2f\ntankbottemp=%.2f\ntanktoptemp=%.2f\npump=%s\n}" % (col, bottom, top, pump)

       # use an exception handler; if the network is down this command will fail
       try:
          #xap.sendHeatBeat(180)
          xap.sendSolarEventMsg( msg )
       except:
          print "Failed to send xAP, network may be down"
      
    else:
       print "No value captured"

    # wait another 45 seconds before attempting another read
    sleep(45)

Xap("FF000F00","shawpad.ujog.solar").run(solar)

