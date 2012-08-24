#!/bin/sh

# need to allow all users to rd/wr to the dmx device
echo 'KERNEL=="dmx*" MODE="0666"' > 10-dmx.rules
sudo mv 10-dmx.rules /etc/udev/rules.d

