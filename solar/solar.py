#!/usr/bin/env python
# Water Solar Collector Readings Logger
# Grabs information from the vbus console and post xap to the Network
 
# code located on http://code.google.com/p/my-jog-home
# reference code for vbusdecode from http://code.google.com/p/vbusdecode/
# reference code for hah/xap from http://code.google.com/p/livebox-hah/

import sys
sys.path.append('../xap')
sys.path.append('../include')

from xaplib import Xap
from time import localtime, strftime, sleep
from sp_keys import *

import serial
import binascii
import subprocess 
import re
import syslog
import eeml

# sequence / process
# uses vbusdecode compiled c from vbusdecode on google code projects (thanks)
# check for new solar reading every 45 seconds
# if values have changed from previous, post a new xapEvent
# if no events have been posted for 3 new readings then post an xapInfo packet
# need to generate heatbeat events - need to work out how often to send them

# use TStats Feed for debug

# need to keep some old values, so as not to dump event when no change in values
pCol=0
pBottom=0
pTop=0
pPump=0

# pachube / cosm
# API_KEY='moved to include file'
COSM_API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = COSM_FEED_SHAWPAD)


syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

def solar(xap):
    global pBottom
    global pCol
    global pTop
    global pPump
    
    s = serial.Serial("/dev/ttyUSB1")

    # test - read 100 bytes from serial port and print out (non formatted, thus garbled
    line = s.read(100)

    # convert to ascii 
    # print binascii.hexlify(line)

    # close the serial port as it won't be used for 5 secs
    s.close()

    # decode the line, at the moment, system calling the vbusdecode binary, 
    # should really put the decode in python
    vb = subprocess.Popen(["./vbusdecode_pi", "0,15,0.1", "2,15,0.1", "4,15,0.1", "6,15,0.1", "8,7,1", "9,7,1"],  stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
    result = vb.communicate(line)[0]

    # make sure only one frame is present from decode
    # result = result[:26]
    # print result

    # split the results into their core parts
    if len(result)>20 :
       	col, bottom, top, sp4, pump, sp1 = re.split('\ +',result,5)

       	col=float(col)
       	bottom=float(bottom)
       	top=float(top)
	pump=float(pump)
      	if pump>0 :
         pump="On"
       	else :
         pump="Off"

       	# adjust collector for -ve
       	if col>600:
            print "Col -ve value: %2.1f\n" % col
            col=(col-6550.6)*-1

       

       	print "Captured reading: ",
       	print "col=",col, " bot=",bottom, " top=",top, " pump=",pump,

	print "Sending xAPs.."

	# open up your cosm feed
        pac = eeml.Pachube(COSM_API_URL, COSM_API_KEY)

       	# top
	msg = "input.state\n{\ntext=%2.1f\n}" % top

	try:
            if pTop!=top:
                xap.sendInstanceEventMsg( msg, "tanktop.temp")
	    	pac.update([eeml.Data(11, top, unit=eeml.Celsius())])
            else:
                xap.sendInstanceInfoMsg( msg, "tanktop.temp")
	except:
          print "Failed to send xAP, network may be down"

	# bottom
	msg = "input.state\n{\ntext=%2.1f\n}" % bottom

	try:
            if pBottom!=bottom:
                xap.sendInstanceEventMsg( msg, "tankbot.temp")
  	    	pac.update([eeml.Data(10, bottom, unit=eeml.Celsius())])
            else:
                xap.sendInstanceInfoMsg( msg, "tankbot.temp")
       	except:
          print "Failed to send xAP, network may be down"

	# collector temp
	msg = "input.state\n{\ntext=%2.1f\n}" % col

	try:
            if pCol!=col:
                xap.sendInstanceEventMsg( msg, "collector.temp")
	     	pac.update([eeml.Data(9, col, unit=eeml.Celsius())])
            else:
		xap.sendInstanceInfoMsg( msg, "collector.temp")
       	except:        
          print "Failed to send xAP, network may be down"

	# pump state
	msg = "input.state\n{\nstate=%s\n}" % pump
    
	try:
            if pPump!=pump:
                xap.sendInstanceEventMsg( msg, "pump")
            	pac.update([eeml.Data(12, pump, unit=eeml.Unit('Binary','derivedUnits','B'))])
            else:
                xap.sendInstanceInfoMsg( msg, "pump")
	except:
        	print "Failed to send xAP, network may be down"

        pTop=top
        pBottom=bottom
        pCol=col
        pPump=pump

	# send data to cosm
	try:
		pac.put()
	except:
		print "Failed to update COSM, network may be down"

    else:
       print "No value captured"

    # wait another 45 seconds before attempting another read
    sleep(45)

syslog.syslog(syslog.LOG_INFO, 'Processing started')

Xap("F4060F01","shawpad.ujog.solar").run(solar)

