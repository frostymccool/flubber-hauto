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

# hm_lock(state, node=99)
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
