#!/bin/sh

git clone git://github.com/lowlander/dmx_usb_module.git
cd dmx_usb_module
make
sudo cp ./dmx_usb.ko /lib/modules/$(uname -r)/kernel/drivers/usb/serial
sudo depmod
echo "dmx kernel module installed"
sudo rm -rf dmx_usb_module
