#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'hobbut'

import tornado.ioloop
import tornado.web
import json
import traceback
# import serial
import logging
# import re

# import kkmdrv
# import er
import driver

import settings


class KKMDriverHandler(tornado.web.RequestHandler):

    def post(self, func_name):
        self.add_header("Content-Type", "application/json; charset=utf-8")
        try:
            logging.info(func_name)
            logging.info(self.request.body)

            if hasattr(self.application.driver, func_name):
                func = getattr(self.application.driver, func_name)
            else:
                raise StandardError('No such method {}'.format(func_name))

            data = json.loads(self.request.body) if self.request.body else {}
            func(**data)
        except driver.Error as e:
            traceback.print_exc()
            error_str, error_code = e.args
            logging.exception(e)
            error = {"status": 'error',
                     'errorText': error_str,
                     'errorCode': error_code}
            self.__write(error)
        except Exception as e:
            traceback.print_exc()
            logging.exception(e)
            error = {"status": 'error',
                     'errorText': str(e),
                     'errorCode': -1}
            self.__write(error)
        else:
            self.__write({'status': 'ok'})
        finally:
            self.finish()

    def __write(self, data={}):
        self.write(json.dumps(data,
                              ensure_ascii=False,
                              encoding='utf-8'))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/([^/]+)/?", KKMDriverHandler),
        ]
        conf = dict(
            template_path='templates',
            static_path='static',
            debug=True,
            autoreload=True,
        )

        import time
        time.sleep(1)
        self.driver = driver.Driver(settings.KKM['PORT'],
                                    settings.KKM['BAUDRATE'])

        # self.driver.cash_income(0)
        # DEBUG
        if 0:
            import mock
            self.kkm = mock.MagicMock()

        tornado.web.Application.__init__(self, handlers, **conf)

if __name__ == "__main__":
    application = Application()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
