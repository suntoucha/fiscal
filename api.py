#!/usr/bin/python
# -*- coding: utf8 -*-

import settings
import logging
import serial

import cdxSHTRIX as kkm
from cdxSHTRIX import cash_income, cash_outcome
from cdxSHTRIX import cancel_check
from cdxSHTRIX import open_drawer

kkm.PORT = settings.KKM['PORT']
ser = None


def print_report(close=None):
    if close:
        kkm.report_z()
    else:
        kkm.report_x()


def print_check(cash, items=None, mode=''):
    # ну тут короче надо будет поморочиться
    if not items:
        items = []

    logging.debug(items)

    logging.debug((
        cash,
        [tuple(map(i.get, ['text', 'qty', 'price'])) for i in items]
    ))

    logging.debug(
        kkm.check(
            cash,
            [tuple(map(i.get, ['text', 'qty', 'price'])) for i in items]
        )
    )

    return
    global ser
    if not ser:
        ser = serial.Serial(
            kkm.PORT,
            kkm.BAUDRATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.7,
            writeTimeout=0.7
        )
    else:
        pass
        # ser.close()
        # ser = serial.Serial(
        #     kkm.PORT,
        #     kkm.BAUDRATE,
        #     parity=serial.PARITY_NONE,
        #     stopbits=serial.STOPBITS_ONE,
        #     timeout=0.7,
        #     writeTimeout=0.7
        # )

    is_check_opened = False
    try:
        kkm.open_check(ser, ctype=0)
        is_check_opened = True
        is_drawed_opened = True
        for item in items:
            kkm.sale(
                ser,
                item['qty'],
                item['price'],
                item['text'][:40],
                taxes=[2, 0, 0, 0]
            )
        if mode == 'plastic':
            is_drawed_opened = False
            kkm.close_check(
                ser,
                summa=0,
                summa2=cash,
                text="------------------------------",
                taxes=[0, 2, 0, 0]
            )
        else:
            kkm.close_check(
                ser,
                summa=cash,
                text="------------------------------",
                taxes=[2, 0, 0, 0]
            )
        if is_drawed_opened:
            kkm.open_drawer(ser)
    except:
        if is_check_opened is True:
            kkm.cancel_check(ser)
        raise

# def print_report(close=None):
#     if close:
#         self.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
#     else:
#         self.kkm.reportWoClose(kkmdrv.DEFAULT_ADM_PASSWORD)


if __name__ == '__main__':

    if 0:
        import serial

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
        # sfrk.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)

        kkm = sfrk.kkm

        kkm.cashIncome(3.3)

    if 0:
        # import cdxATOL as kkm
        # import cdxGEPARD as kkm

        # kkm.put_sum(20)
        # kkm.cmdX()


        ser = serial.Serial(
            "/dev/tty.fiscal", 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.7,
            writeTimeout=1.7,
        )



        print kkm.get_kkm_no()

    # print 'hahah'
