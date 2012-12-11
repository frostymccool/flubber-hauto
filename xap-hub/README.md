xAP Hub for RaspberryPi
=======================

This application was based on the "xAP Compliant Hub" from Patrick Lidstone.

With this version some improvements were introduce to work on Raspberry Pi hardware. The old code from Patrick Lidstone is also included.


How it works:
=============

The application first load the xAP settings from the xap-hub.xml file. After that discover the network settings (IP address, netmask, gateway) and setup several a socket to listen for incoming messages from any address at port 3639 by default, another socket to broadcast heartbeats to the network at broadcast    address (for example 192.168.1.255) and a third socket to send the incoming    messages from the network to the connected clients at address 127.0.0.1 with    the associated port for each client.

The received messages are filtered and relayed to the clients, also the messages from the clients are relayed to the other clients.


Setup:
======

Compile with supplied makefile.

The xAP settings can be loaded from the xap-hub.xml file. In hub.h you can configure the path to this file, by default the application look for the xml file in the same folder than the executable.


Usage:
======

Usage: xap-hub [interface] [debug level]

e.g. "xap-hub eth0" 
which uses interface eth0 

or "xap-hub"
which uses default interface eth0

Debug level = 0-off; 1-info; 2-verbose; 3-debug


License:
========

Copyright (c) Jose Luis Galindo, 2012.
Copyright (c) Patrick Lidstone, 2002.
   
No commercial use.
No redistribution at profit.
All derivative work must retain this message and
acknowledge the work of the original author.  

Please report defects to support@homected.com
Original code from patrick@lidstone.net attached in zip file.


Last revision: 
==============

28th Nov 2012: Ian Shaw: Jose source in oldsrc/Jose, updates for Flubber in src
original extraction from github https://github.com/homected/xap-hub.git

28 March 2012 by Jose Luis Galindo (support@homected.com)
