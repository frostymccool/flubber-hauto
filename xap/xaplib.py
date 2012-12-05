#!/usr/bin/env python
#
# XAP support library
#
# brett@dbzoo.com
#
# Updated for flubber
# ian@shawpad.com

import socket, traceback, time

class Xap:
	def __init__(self, uid, source):
		self.heartbeat_tick = 0;
		self.uid = uid
		self.source = source
        self.sourceInstance = ""
		self.port = 0
		self.running = 1

	def run(self, func):
		self.connect()
		while self.running:
			if self.port:
				self.heartbeat(60)
        # add receive buffer check here
			try:
				func(self)
        # loop checking receive buffer and heartbeat while waiting for next time to run func
			except KeyboardInterrupt:
				self.done()
				pass
			except socket.timeout:
				pass
			except:
				traceback.print_exc()
				self.done()

	def done(self):
		self.gout.close()
		self.gin.close()
		self.running = 0

	def connect(self):
		host = ''
		self.gin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.gin.settimeout(60)
		try:
			self.gin.bind((host, 3639))
		except socket.error, msg:
			print "Broadcast socket port 3639 in use"
			print "Assuming a hub is active"
			host = '127.0.0.1'
			for self.port in range(3639,4639):
				try:
					self.gin.bind((host, self.port))
				except socket.error, msg:
					print "Socket port %s in use" % self.port
					continue
				print "Discovered port %s" % self.port
				break

		self.gout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.gout.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def send(self ,msg):
#                print "msg:", " port:",self.port
		self.gout.sendto(msg, ('<broadcast>', 3639))

	def sendMsg(self, clazz, target, msg, sourceInstance):
		msg = """xap-header
{
v=12
hop=1
uid=%s
class=%s
source=%s%s
}
%s""" % (self.uid, clazz, self.source, sourceInstance, msg)
		self.send(msg)

	def sendLCDMsg(self, msg):
		msg = "output.state.1\n{\nid=*\ntext=%s\n}" % msg
		self.sendMsg("xAPBSC.cmd","dbzoo.livebox.Controller:lcd", msg)
	
	def sendSMS(self, num, msg):
		msg = "outbound\n{\nnum=%s\nmsg=%s\n}" % (num, msg)
		self.sendMsg("sms.message","dbzoo.livebox.sms", msg)

	def sendInfoMsg(self, msg):
		self.sendMsg("xAPBSC.info", "", msg)

	def sendEventMsg(self, msg):
		self.sendMsg("xAPBSC.event", "", msg)

	def sendSolarEventMsg(self, msg):
		self.sendMsg("solar.event", "", msg)

	def sendHeatingEventMsg(self, msg, sourceInstance):
        if len(sourceInstance)>0:
            sourceInstance = ":%s" % sourceInstance
		self.sendMsg("xAPBSC.event", "", msg, sourceInstance)

	def receive(self):
		try:
			return self.gin.recvfrom(8192)
		except KeyboardInterrupt:
			self.done()
			pass

# The HUB won't relay messages to us until it see's our heartbeat knows our listening port.
# This must be periodically sent to keep it active on the HUB.
	def heartbeat(self, interval):
		now = time.time()
		if now - self.heartbeat_tick > interval or self.heartbeat_tick == 0:
			self.heartbeat_tick = now
			msg="""xap-hbeat
{
v=12
hop=1
uid=%s
class=xap-hbeat-alive
source=%s
interval=%s
port=%s
}"""
			self.send(msg % (self.uid, self.source, interval, self.port))
