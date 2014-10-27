#!/bin/bash
set -x

reldir=`dirname $0`
cd $reldir
directory=`pwd`
echo "Directory is $directory"


lsusb
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3405", GROUP="fiscal", MODE="0666", SYMLINK+="tty.fiscal"' | sudo tee /etc/udev/rules.d/60-fiscal.rules
sudo modprobe usbserial vendor=0x0483 product=0x3405 
sudo service udev restart

# fuser -k /dev/tty.fiscal;

# source env/bin/activate && pip install requirements.txt
pip install -r requirements.txt

# while true;
# do
    python web.py;
    # echo 'lets try again afer 5 sec'
    # sleep 5
# done;
