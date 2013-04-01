#!/usr/bin/env python
# Current Cost Envir logger
# Grabs Main Electricity, temperature and remote units

# code located on http://code.google.com/p/my-jog-home
# created from reference: http://naxxfish.eu/2012/electricity-usage-logging-with-currentcost-envir-and-a-raspberry-pi/

import sys
sys.path.append('../xap')
sys.path.append('../include')

from xaplib import Xap
from time import localtime, strftime, sleep
from sp_keys import *

import xml.etree.ElementTree as ET
import os
import serial
import binascii
import subprocess
import re
import syslog
import eeml

# pachube / cosm
# API_KEY='moved to include file'
COSM_API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = COSM_FEED_SHAWPAD)

syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

temperatureCurrent=0
temperaturePrevious=0
SensorCurrent=range(4)
SensorPrevious=range(4)
changed=0
readingsTaken=0

#Name, Sensor ID, COSM ID
SensorList=[
["Main", 0, 1],
["SqueezyPi", 2, 4],
["HotWaterTap", 1, 3],
["Washing Machine", 3, 6],
]

# COSM feed ID for the envir temperature value
COSM_ID_TEMP=2

syslog.syslog(syslog.LOG_INFO, 'Processing started')

ser = serial.Serial('/dev/ttyUSB2',57600 )

# open up  cosm feed
pac = eeml.Pachube(COSM_API_URL, COSM_API_KEY)

line = ""
while 1:
  try:
    x = ser.read()
    line = line + x
    if (x == "\n"):
        # parse that line!
        tree = ET.fromstring(line)
        line = ""
        type = tree.find('type')
        if type is None or type.text != '1':
            print "Received non-realtime sensor packet: %s" % line
            continue
        sensor = int(tree.find('sensor').text)
        #print "\n --- Received packet from sensor %d" % sensor
        temp = tree.find('tmpr').text
        if tree.find('ch1') is not None:
            ch1 = tree.find('ch1')
            ch1_watts = int(ch1.find('watts').text)
    
        print "Sensor %d: %dW, %sC" % (sensor, ch1_watts, temp)

        if SensorPrevious[sensor]!=ch1_watts:
            SensorCurrent[sensor]=ch1_watts
            SensorPrevious[sensor]=ch1_watts
            changed=1

            # Add data for COSM
            for element in SensorList:
                if element[1] == sensor:
                    pac.update([eeml.Data(element[2], SensorCurrent[element[1]], unit=eeml.Watt())])

        if temperaturePrevious!=temp:
            temperatureCurrent=temp
            temperaturePrevious=temp
            # changed=1
                #- not interested in temp change to force COSM as it will get picked up on other change anyway
            
            # Add data for COSM
            pac.update([eeml.Data(COSM_ID_TEMP, temp, unit=eeml.Celsius())])
                
        # Upload data to COSM every x samples
        if changed and ((readingsTaken % 10 ==0) or (readingsTaken<10)):
            print "New Values to COSM %d" % (readingsTaken %30)
            pac.put()
            changed=0

        readingsTaken+=1
  except:
    print "Issue with capture element"
    syslog.syslog(syslog.LOG_ERR, 'Exception thrown during loop')

