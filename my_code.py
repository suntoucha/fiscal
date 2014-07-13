# -*- encoding: utf-8 -*-
import api
import serial
import kkmdrv
# import re

import settings
import cdxSHTRIX as kkm
# import cdxATOL as kkm
# import cdxGEPARD as kkm
kkm.PORT = settings.KKM['PORT']


if 1:
    # kkm.cmdSumIN(123.45)
    # for i in range(10):
    #     kkm.cmdPrint(u'Привет4')

    # kkm.cmdPrint(u'Привет4')
    # kkm.cmdSumIN(123.45)
    # kkm.beep()
    # kkm.cmdGetDT()
    # kkm.cmdGetKkmNo()

    kkm.get_kkm_no()

    # kkm = kkm.receipt(
    #     100,
    #     [
    #         (u'Товар1', 1, 1.23),
    #         (u'Товар2', 2, 0.60),
    #         (u'Товар3', 3, 0.41)
    #     ],
    #     7
    # )

if 0:
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

    kkm = kkmdrv.KKM(
        ser,
        password=kkmdrv.DEFAULT_PASSWORD,
    )
    kkm.test()
    # print sfrk.getStatusString()
    # sfrk.kkm.cashIncome(23.0)

    # print sfrk.kkm.cashIncome(234.0)
    # print sfrk.kkm.cashIncome(234.0)
    # print kkm.__clearAnswer()
    # print dir(sfrk.kkm)
    # print sfrk.kkm.__sendCommand(0x00, kkmdrv.DEFAULT_PASSWORD)
    # print sfrk.kkm.__readAnswer()


if 0:
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
