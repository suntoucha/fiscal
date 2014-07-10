for i in range(110):
    # code...
    print 'hahah'

import serial
import kkmdrv

ser = serial.Serial(
    "/dev/tty.fiscal", 115200,
    # "/dev/hidraw0", 115200,
    # "/dev/ttyS0", 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.7,
    writeTimeout=1.7
)


sfrk = kkmdrv.ShtrihFRK(kkmdrv.DEFAULT_PASSWORD,
                        kkmdrv.DEFAULT_ADM_PASSWORD,
                        ser)

# kkm = kkmdrv.KKM(ser,
#                  kkmdrv.DEFAULT_PASSWORD)
# kkm.printString(text='''hahah''')
