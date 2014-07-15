#!/bin/bash
lsusb
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3405", GROUP="fiscal", MODE="0666", SYMLINK+="tty.fiscal"' | sudo tee /etc/udev/rules.d/60-fiscal.rules
sudo modprobe usbserial vendor=0x0483 product=0x3405 
sudo service udev restart
reldir=`dirname $0`
cd $reldir
directory=`pwd`
echo "Directory is $directory"

echo 'python web.py'
python web.py
