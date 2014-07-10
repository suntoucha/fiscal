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
import settings

PASSWORD = "1231231qweqweqwe"


class KKMHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.kkm = self.application.kkm

    def prepare(self):
        password = self.get_argument("password", default=None)
        if PASSWORD != password:
            self.error("incorrect_password")

    def post(self):
        self.add_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(dict))
        return
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

    def __write(self, dict={}):
        self.write(json.dumps(dict))
        self.finish()


class PrintReport(KKMHandler):
    def postJson(self, data):
        if data.get("close"):
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
                self.kkm.Sale(item['qty'],
                              item['price'],
                              item['text'][:40],
                              taxes=[2, 0, 0, 0])
            if 'mode' in data and data['mode'] == 'plastic':
                open_drawer = False
                self.kkm.closeCheck(summa=0,
                                    summa2=data['cash'],
                                    text="------------------------------",
                                    taxes=[0, 2, 0, 0])
            else:
                self.kkm.closeCheck(summa=data['cash'],
                                    text="------------------------------",
                                    taxes=[2, 0, 0, 0])
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


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/check/print/", PrintCheck),
            (r"/api/check/cancel/", CancelCheck),
            (r"/api/report/", PrintReport),
            (r"/api/cash/income/", CashIncome),
            (r"/api/cash/outcome/", CashOutcome),
            (r"/api/drawer/open/", OpenCashDrawer),
        ]
        conf = dict(
            template_path='templates',
            static_path='static',
            debug=True,
            autoreload=True,
        )

        if conf['debug']:
            import mock
            self.kkm = mock.MagicMock()
        else:
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
            sfrk.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
            self.kkm = sfrk.kkm

        tornado.web.Application.__init__(self, handlers, **conf)


if __name__ == "__main__":
    application = Application()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
