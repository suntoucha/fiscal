# -*- encoding: utf-8 -*-
import api
import serial
import kkmdrv
import re
import settings

if 1:
    func_name = 'hello'
    data = {
        'name': 'zoi',
        'address': 'hahaha',
    }

    if hasattr(api,func_name):
        print getattr(api, func_name)(**data)


    ser = serial.Serial(
        "/dev/tty.fiscal", 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.7,
        writeTimeout=1.7,
    )
    sfrk = kkmdrv.ShtrihFRK(kkmdrv.DEFAULT_PASSWORD,
                            kkmdrv.DEFAULT_ADM_PASSWORD,
                            ser)

    # print sfrk.getStatusString()
    print sfrk.kkm.cashIncome(234.0)


def camel_to_underscore(name):
    name = name[0].lower() + name[1:]
    camel_pat = re.compile(r'([A-Z])')
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)

def underscore_to_camel(name):
    under_pat = re.compile(r'_([a-z])')
    return under_pat.sub(lambda x: x.group(1).upper(), name)

print camel_to_underscore('ReportWClose')
print underscore_to_camel('report_w_close')


if 0:
    import kkm
    kkmDev = kkm.Atol.AtolKKM(
        {
            'port': '/dev/tty.fiscal',
            'baudrate': 115200
        }
    )

    # name = 'dfjdkf'
    # price = 3434.0
    # count = 33.0


    kkmDev.OpenCheck()
    # # kkmDev.Sell(name.strip(),
    # #             Decimal(price.strip()),
    # #             Decimal(count.strip()),
    # #             0)
    # # kkmDev.Discount(discount, kkm.kkm_Check_dis)
    # kkmDev.Payment(payment)


    kkmDev.PrintToDisplay('\x0C')
    kkmDev.PrintToDisplay('')
    max = kkmDev.getDisplayStringMax()
    kkmDev.PrintToDisplay('Спасибо'.center(max))
    kkmDev.PrintToDisplay('за покупку!'.center(max))
