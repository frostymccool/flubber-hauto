#
#
#
#
import serial
from struct import pack
import time
import sys
import os
sys.path.append('../xap')

from xaplib import Xap
from stats_defn import *
from hm_constants import *
from hm_utils import *

# these will be crated as an array

#    def SetxAPNodeTemp(temperature, serport, xap, holdtime=0):
#    def SetNodeTemp(temperature, serport, holdtime=0):
#    def GetxAPNodeTemp(temperature, serport, xap, holdtime=0):
#    def GetNodeTemp(serport)
#    def GetTargetNodeTemp(serport)

#    def readTStatStatus(serport,force=0)
#    def mapdata(datal):

class thermostat:
    " class to handle data set for each instance of a t-stat"
    def __init__(self, address, shortName, longName, protocol, instanceID, UID):
        serf.initialised = 0 # flag to indicate that initial data set not read yet
        self.definedaddress = address
        self.xAPInstanceID = instanceID
        self.xAPUID = UID
        self.protocol = protocol
        self.shortName = shortName
        self.longName = longName
        
        self.DATAOFFSET = 9
        self.GET_TEMP_CMD=38
        self.SET_TEMP_CMD=18
        
        # t-stat payload data
        self.off=0
        self.demand=0  # current demand i.e. flame on
        self.currenttemp=0
        self.lastxAPcurentTemp=0
        self.targettemp=0
        self.sensormode=0

        self.model =0
        self.tempformat =0
        self.frostprotectionenable =0
        self.frosttemp =0
    
    
        ## need to add the rest of the data structure.......
    
    # set demand temp and post xAP message
    # checking for demand changes and using event / info appropriately
    def SetxAPNodeTemp(temperature, serport, xap, holdtime=0):
        
        # create the xap message ready
        msg = "input.state\n{\ntext=%2.1f\n}" % temperature

        try:
            # event or info?
            if (temperature!=self.targettemp):
                SetNodeTemp(temperature, serport, holdtime)

                # now temp set handle the xap message post
                
        ## TODO: need extra handler as the xap handler could have error and if we are here then the t-stat has already had it's demand temperature updated
                
                xap.sendInstanceEventMsg( msg, self.xAPInstanceid )
                self.targettemp=temperature
            else:
                # no need to send new request to t-stat as the current demand is still accurate
                xap.sendInstanceInfoMsg( msg, self.xAPInstanceid )

        except:
            print "Failure to SetxAPNodeTemp(%d) on tstat address %d" % (temperature, self.definedaddress)
            raise "SetxAPNodeTemp(%d) failed for node: %d" % (temperature, self.definedaddress)

                
                

    # set demand temperature with optional hold time
    def SetNodeTemp(temperature, serport, holdtime=0):
        payload = [temperature]
    
        msg = hmFormMsgCRC(self.definedaddress, node[SL_CONTR_TYPE], MY_MASTER_ADDR, FUNC_WRITE, SET_TEMP_CMD, payload)
    
        print msg
        string = ''.join(map(chr,msg))
    
        if (hm_sendwritecmd(self.definedaddress, string, serport)==1):
            print "Failure to SetNodeTemp to %d on tstat address %d" % (temperature,self.definedaddress)
            raise "SetNodeTemp failed for node: %d" % self.definedaddress
        else:
            self.roomsettemp = temperature



    # set demand temp and post xAP message
    # checking for demand changes and using event / info appropriately
    def GetxAPNodeTemp(serport, xap):
    
        try:
            GetNodeTemp(serport)
        
            # now temp get handle the xap message post
        
            # create the xap event
            msg = "input.state\n{\nstate=%d\ntext=%2.1f\n}" % (self.demand, self.currenttemp)
            #print msg
        
            # event or info?
            if (self.currenttemp!=self.lastxAPcurentTemp):
                xap.sendInstanceEventMsg( msg, self.xAPInstanceid )
                self.lastxAPcurentTemp=self.currenttemp
            else:
                xap.sendInstanceInfoMsg( msg, self.xAPInstanceid )
    
        except:
            print "Failure to GetxAPNodeTemp() on tstat address %d" % (self.definedaddress)
            raise "GetxAPNodeTemp() failed for node: %d" % (self.definedaddress)

        return self.currenttemp
                
                
    # get current t-stat temperature
    def GetNodeTemp(serport):
                
        ReadTStatStatus(serport)
        print "Current Temperature: %.1f" % self.currenttemp
        return self.currenttemp
                
    # get target t-stat temperature
    def GetTargetNodeTemp(serport):
        ReadTStatStatus(serport)
        print "Target Temperature: %.1f" % self.targettemp
        return self.targettemp

    def ReadTStatStatus(serport,force=0):
        # read and update all the status for the t-stat also
        # TODO: use a timer, if cache data still current for 3 mins, the don't read, just use cached data
        payload = []
            
        try:
            payload = hm_sendreadcmd(self.definedaddress, serport)
            # parse the payload to extract the current temp
            self.mapdata(payload)
            
        except:
            print "Failure to ReadTStatStatus() on tstat address %d" % (self.definedaddress)
            raise "ReadTStatStatus failed for node: %d" % self.definedaddress

            
    # call this routine with a datablock read from the serial port to update all the status in the class
    def mapdata(datal):
        "check the address in the payload is this instance address"
        address = datal[11+ DATAOFFSET]
        if (self.definedaddress!=address):
            raise "Invalid Address in payload provided (%d), should be %d for this class instance" % (address, self.definedaddress)
        
        self.model = datal[4+ DATAOFFSET] # (DT/DT-E/PRT/PRT-E) (00/01/02/03)
        self.tempformat = datal[5+ DATAOFFSET]  # C=0 F=1

        self.frostprotectionenable = datal[7+ DATAOFFSET]
        self.frosttemp = datal[17+ DATAOFFSET] # frost protect temperature default 12
        #cal_h=datal[8+ DATAOFFSET]
        #cal_l = datal[9+ DATAOFFSET]
        #self.caloffset = (cal_h*256 + cal_l)

        self.outputdelay = datal[10+ DATAOFFSET]
        
        self.optimstart = datal[14+ DATAOFFSET]
        self.rateofchange = datal[15+ DATAOFFSET]
        self.targettemp = datal[18+ DATAOFFSET]
        self.off = datal[21+ DATAOFFSET]
        self.keylock = datal[22+ DATAOFFSET]
        self.runmode = datal[23+ DATAOFFSET]

        holidayhourshigh = datal[24+ DATAOFFSET]
        holidayhourslow = datal[25+ DATAOFFSET]
        self.holidayhours = (holidayhourshigh*256 + holidayhourslow)

        tempholdminshigh = datal[26+ DATAOFFSET]
        tempholdminslow = datal[27+ DATAOFFSET]
        self.tempholdmins = (tempholdminshigh*256 + tempholdminslow)
        
        # if sensormode is 0 then use air sensor, otherwise 2 is floortemp
        # these are the only 2 we are using in our system
        self.sensormode = datal[13+ DATAOFFSET] # air / remote / floor
        if self.sensormode==0:
            tempsenseoffset+=2
        else:
            tempsenseoffset=0
        temphigh = datal[30+tempsenseoffset+ DATAOFFSET]
        templow  = datal[31+tempsenseoffset+ DATAOFFSET]
        self.currenttemp = (temphigh*256 + templow)/10.0
    
        self.errcode = datal[34+ DATAOFFSET]
        self.demand = datal[35+ DATAOFFSET] # 1 = currently heating

        self.currentday = datal[36+ DATAOFFSET]
        self.currenthour = datal[37+ DATAOFFSET]
        self.currentmin = datal[38+ DATAOFFSET]
        self.currentsec = datal[39+ DATAOFFSET]

        self.progmode = datal[16+ DATAOFFSET] # 0 = 5/2
        self.wday_t1_hour = datal[40+ DATAOFFSET]
        self.wday_t1_mins = datal[41+ DATAOFFSET]
        self.wday_t1_temp = datal[42+ DATAOFFSET]
        self.wday_t2_hour = datal[43+ DATAOFFSET]
        self.wday_t2_mins = datal[44+ DATAOFFSET]
        self.wday_t2_temp = datal[45+ DATAOFFSET]
        self.wday_t3_hour = datal[46+ DATAOFFSET]
        self.wday_t3_mins = datal[47+ DATAOFFSET]
        self.wday_t3_temp = datal[48+ DATAOFFSET]
        self.wday_t4_hour = datal[49+ DATAOFFSET]
        self.wday_t4_mins = datal[50+ DATAOFFSET]
        self.wday_t4_temp = datal[51+ DATAOFFSET]
        self.wend_t1_hour = datal[52+ DATAOFFSET]
        self.wend_t1_mins = datal[53+ DATAOFFSET]
        self.wend_t1_temp = datal[54+ DATAOFFSET]
        self.wend_t2_hour = datal[55+ DATAOFFSET]
        self.wend_t2_mins = datal[56+ DATAOFFSET]
        self.wend_t2_temp = datal[57+ DATAOFFSET]
        self.wend_t3_hour = datal[58+ DATAOFFSET]
        self.wend_t3_mins = datal[59+ DATAOFFSET]
        self.wend_t3_temp = datal[60+ DATAOFFSET]
        self.wend_t4_hour = datal[61+ DATAOFFSET]
        self.wend_t4_mins = datal[62+ DATAOFFSET]
        self.wend_t4_temp = datal[63+ DATAOFFSET]
