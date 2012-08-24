#!/bin/sh

# add lines to the blacklist file such that the dmx driver can load instead of the ttyUSB
# for Raspberry Pi the filename must have a .conf, not plain blacklist as referenced in ola build doc
# for the dmx adapters I'm using blacklisting just the ftio_sio works

filebase="blacklist.conf"
filename="/etc/modprobe.d/blacklist.conf"
if [! -e $filename ];
then
echo "blacklist file exists, adding to it"
#sed -i '$a blacklist usbserial' $filename
#sed -i '$a blacklist usb-serial' $filename
sed -i '$a blacklist ftdi_sio' $filename
else
echo "blacklist file doesn't exists, creating it"
echo 'blacklist ftdi_sio' > $filebase
#sed -i '$a blacklist usb-serial' $filebase
#sed -i '$a blacklist usbserial' $filebase
sudo mv $filebase $filename
fi

