Для правильной установки USB serial необходимо сделать следующее (для Ubuntu):

```
$ sudo modprobe usbserial vendor=0x0483 product=0x3405
```

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


Kill process that raises Device or resource busy: '/dev/ttyUSB0'?

```
$ sudo fuser -k /dev/tty.fiscal
```


Основные команды
```
$ http post localhost:8888/api2/cash/income/ summ:=23
$ http post localhost:8888/api2/cash/outcome/ summ:=23
$ http post localhost:8888/api2/report/
$ http post localhost:8888/api2/report/ close:=1
```


##что написать что бы поднялось
```
$ git clone https://github.com/morentharia/fiscal.git
$ sudo apt-get install python-pip
$ sudo pip install -r requirements.txt

```

ожидаем появления 
`Bus 001 Device 005: ID 0483:3405 SGS Thomson Microelectronics`

```
$ lsusb
Bus 001 Device 002: ID 0424:9512 Standard Microsystems Corp. 
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. 
Bus 001 Device 005: ID 0483:3405 SGS Thomson Microelectronics 
Bus 001 Device 004: ID 148f:5370 Ralink Technology, Corp. RT5370 Wireless Adapter
```

```
$ echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3405", GROUP="fiscal", MODE="0666", SYMLINK+="tty.fiscal"' | sudo tee /etc/udev/rules.d/60-fiscal.rules
$ sudo modprobe usbserial vendor=0x0483 product=0x3405 
$ sudo service udev restart
```


