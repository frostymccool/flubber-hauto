#!/usr/bin/env python
# trigger on heating info or cmd messages
#
# for each heating event capture event / info message states
# need to cater for all elements in the stat_defn

# read the t-stats list
# setup triggers for info,event and cmd bsc messages
# info request messages can simply return the current temp status
# cmd messages needs to kick off a temp change
# info and event messages (driven from the polling process) needs to maintain a copy of the current temp etc.
# xAPBSC.cmd, xAPBSC.query

import sys
sys.path.append('../xap')

from xaplib import Xap
import syslog
import re

# example
# {
# source=UKUSA.xAPFlash.joggler
# target=shawpad.rpi.heating:breakfastbar.temp
# }
# request
# {
# }

triggerQuery = ["source=shawpad.rpi.heating", "class=xAPBSC"] # query - using info for testing
trgcntQ = len(triggerQuery)
triggerCmd = ["source=shawpad.rpi.heating", "class=xAPBSC.cmd"]
trgcntC = len(triggerCmd)

#syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_SYSLOG)

def servicexAPStack(xap):
    if 0:
        print "<<<<Service xap messages...>>>>\n"


def monitorHeating(xap):
    message, address = xap.receive()
    
    # check for Query Message
    if len(filter(lambda xap: message.find(xap) != -1, triggerQuery)) == trgcntQ:
        # print message
        # 1 - check the target for wildcard or specific stat request
        # 2 - extract the instance (from the between : and .)
        # 3 - extract the source to create returntarget
        # 4 - use the instance to identify the last temp value
        
        lines = re.split("\n+", message)
        returntarget = filter(lambda m: "source=" in m,lines)
        print returntarget

        newsources = filter(lambda m: "target=" in m,lines)

        #print elements
            
        #xap.SendQueryMsg(returntarget,msg)

    # check for cmd Message
    elif len(filter(lambda xap: message.find(xap) != -1, triggerCmd)) == trgcntC:
        # check the source for wildcard or specific stat request
        print message



# MAIN

#syslog.syslog(syslog.LOG_INFO, 'Processing started')

#Xap("FF000F01","shawpad.rpi.heating.event").run(monitorHeating)
