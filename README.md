Для правильной установки USB serial необходимо сделать следующее (для Ubuntu):

sudo modprobe usbserial vendor=0x0483 product=0x3405

Тогда dmesg|tail должен выдать что то вида:

[ 719.942399] usbcore: registered new interface driver usbserial
[ 719.942648] USB Serial support registered for generic
[ 719.943266] usbserial_generic 2-1:1.0: generic converter detected
[ 719.944256] usb 2-1: generic converter now attached to ttyUSB0
[ 719.944479] usbcore: registered new interface driver usbserial_generic
[ 719.944509] usbserial: USB Serial Driver core 

Теперь к ttyUSB0 можно обращаться как к COM-порту по протоколу Меркурий-MSK


+
прописал в настройках udev
```
# cat /etc/udev/rules.d/60-fiscal.rules 
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3405", GROUP="fiscal", MODE="0666", SYMLINK+="tty.fiscal"
```

после этого у меня появилас ссылка /dev/tty.fiscal и с ней теперь всё ок
такие пироги


> sudo apt-get install lpr
