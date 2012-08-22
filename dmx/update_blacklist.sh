#!/bin/sh

# add lines to the blacklist file such that the dmx driver can load instead of the ttyUSB
$filename ="/usr/local/net/var/lib/directoryservice/sync.disable"
if [-e $filename ];
then
echo "blacklist file exists, adding to it"
sed -i '$a blacklist usbserial' /etc/modprobe.d/blacklist
sed -i '$a blacklist usb-serial' /etc/modprobe.d/blacklist
sed -i '$a blacklist ftdi_sio' /etc/modprobe.d/blacklist
else
echo "blacklist file doesn't exists, creating it"
echo 'blacklist usbserial' > blacklist
sed -i '$a blacklist usb-serial' blacklist
sed -i '$a blacklist ftdi_sio' blacklist
sudo mv blacklist /etc/modprobe.d/
fi

