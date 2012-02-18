#!/usr/bin/env python
# xAP message listener - HUB aware
 
from xaplib import Xap
 
def snoopTraffic(xap):
    print "MSG: %s ADDR: %s" % xap.receive()
 
Xap("FF000F00","dbzoo.livebox.Snoop").run(snoopTraffic)

