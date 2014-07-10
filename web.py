#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'hobbut'

import tornado.ioloop
import tornado.web
import json
import traceback
import serial
import kkmdrv
import logging
import signal

PASSWORD = "1231231qweqweqwe"

class KKMHandler(tornado.web.RequestHandler):
    def initialize(self, kkm):
        self.kkm = kkm

    def prepare(self):
        password = self.get_argument("password", default=None)
        if PASSWORD != password:
            self.error("incorrect_password")

    def post(self):
        try:
            print self.request.body
            data = json.loads(self.request.body)
            self.postJson(data)
        except:
            traceback.print_exc()
            self.error()

    def postJson(self, data):
        pass

    def error(self, msg=None):
        error = {"success": False}
        if msg is not None:
            error["error"] = msg
        self.__write(error)

    def success(self):
        self.__write({"success": True})

    def __write(self, dict = {}):
        self.add_header("Content-Type","application/json")
        self.write(json.dumps(dict))
        self.finish()


class PrintReport(KKMHandler):
    def postJson(self, data):
        if "close" in data and data["close"] == True:
            self.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
        else:
            self.kkm.reportWoClose(kkmdrv.DEFAULT_ADM_PASSWORD)
        self.success()


class CashIncome(KKMHandler):
    def postJson(self, data):
        self.kkm.cashIncome(data["summ"])
        self.success()


class CashOutcome(KKMHandler):
    def postJson(self, data):
        self.kkm.cashOutcome(data["summ"])
        self.success()


class OpenCashDrawer(KKMHandler):
    def postJson(self, data):
        self.kkm.openCashDrawer()
        self.success()


class PrintCheck(KKMHandler):
    def postJson(self, data):
        #TODO data_format_validation
        check_opened = False
        try:
            self.kkm.openCheck(0)
            check_opened = True
            open_drawer = True
            for item in data['items']:
                self.kkm.Sale(item['qty'], item['price'], item['text'][:40], taxes=[2, 0, 0, 0])
            if 'mode' in data and data['mode'] == 'plastic':
                open_drawer = False
                self.kkm.closeCheck(summa=0, summa2=data['cash'], text="------------------------------", taxes=[0, 2, 0, 0])
            else:
                self.kkm.closeCheck(summa=data['cash'], text="------------------------------", taxes=[2, 0, 0, 0])
            if open_drawer:
                self.kkm.openCashDrawer()
            self.success()
        except:
            if check_opened is True:
                self.kkm.cancelCheck()
            raise



class CancelCheck(KKMHandler):
    def postJson(self, data):
        self.kkm.cancelCheck()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

is_closing = False

def signal_handler(signum, frame):
    global is_closing
    logging.info('exiting...')
    is_closing = True


def try_exit():
    global is_closing
    if is_closing:
#        ser.close()
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('exit success')
        resolverProc.terminate()



if __name__ == "__main__":
    ser = serial.Serial(
        "/dev/tty.fiscal", 115200,
        # "/dev/hidraw0", 115200,
        # "/dev/ttyS0", 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.7,
        writeTimeout=1.7
    )
    sfrk = kkmdrv.ShtrihFRK(kkmdrv.DEFAULT_PASSWORD, kkmdrv.DEFAULT_ADM_PASSWORD, ser)
    sfrk.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
    signal.signal(signal.SIGINT, signal_handler)


    data  = {'mode': 'plastic'}
    self.kkm.openCheck(0)
    check_opened = True
    open_drawer = True
    for item in [{'qty':'qty',
                  'price': 'price',
                  'text': 'jlalala',
                  }]:
        self.kkm.Sale(item['qty'], item['price'], item['text'][:40], taxes=[2, 0, 0, 0])
    if 'mode' in data and data['mode'] == 'plastic':
        open_drawer = False
        self.kkm.closeCheck(summa=0, summa2=data['cash'], text="------------------------------", taxes=[0, 2, 0, 0])
    else:
        self.kkm.closeCheck(summa=data['cash'], text="------------------------------", taxes=[2, 0, 0, 0])
    if open_drawer:
        self.kkm.openCashDrawer()

    exit()

    application = tornado.web.Application([
        (r"/api/check/print/", PrintCheck, dict(kkm=sfrk.kkm)),
        (r"/api/check/cancel/", CancelCheck, dict(kkm=sfrk.kkm)),
        (r"/api/report/", PrintReport, dict(kkm=sfrk.kkm)),
        (r"/api/cash/income/", CashIncome, dict(kkm=sfrk.kkm)),
        (r"/api/cash/outcome/", CashOutcome, dict(kkm=sfrk.kkm)),
        (r"/api/drawer/open/", OpenCashDrawer, dict(kkm=sfrk.kkm)),
    ])

    application.listen(8888)
    tornado.ioloop.PeriodicCallback(try_exit, 100).start()

    import subprocess, sys, os
    global resolverProc
    dir = os.path.dirname(os.path.realpath(__file__))
    resolverProc = subprocess.Popen([sys.executable, os.path.join(dir,"resolver.py")])
    if resolverProc.poll() is not None and resolverProc.returncode != 0:
        raise Exception("error start resolver")
    tornado.ioloop.IOLoop.instance().start()
