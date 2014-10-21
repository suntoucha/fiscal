#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'hobbut'

from tornado import gen
import tornado.ioloop
import tornado.web
import toro

import json
import time
import traceback
# import serial
import logging
# import re

# import kkmdrv
# import er
import driver

import settings


DRIVER_LOCK = toro.Lock()


class KKMDriverHandler(tornado.web.RequestHandler):

    # def initialize(self):
    #     self.lock = toro.Lock()

    @gen.coroutine
    def post(self, func_name):
        # self.add_header("Content-Type", "application/json; charset=utf-8")
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            logging.info(func_name)
            logging.info(self.request.body)

            if hasattr(self.application.driver, func_name):
                func = getattr(self.application.driver, func_name)
            else:
                raise StandardError('No such method {}'.format(func_name))

            data = json.loads(self.request.body) if self.request.body else {}

            with (yield DRIVER_LOCK.acquire()):
                logging.debug('LOCK acquire')
                assert DRIVER_LOCK.locked()
                func(**data)

            logging.debug('LOCK release')
            assert not DRIVER_LOCK.locked()

        except driver.Error as e:
            traceback.print_exc()
            error_str, error_code = e.args
            logging.exception(e)
            error = {"status": 'error',
                     'errorText': error_str,
                     'errorCode': str(error_code)}
            self.__write(error)
        except Exception as e:
            traceback.print_exc()
            logging.exception(e)
            error = {"status": 'error',
                     'errorText': str(e),
                     'errorCode': str(-1)}
            self.__write(error)
        else:
            self.__write({'status': 'ok'})
        finally:
            self.finish()

    def __write(self, data={}):
        self.write(json.dumps(data,
                              ensure_ascii=False,
                              encoding='utf-8'))


class GetMacAddressHandler(tornado.web.RequestHandler):
    def get(self, ifname=None):
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            if not ifname:
                ifname = 'eth0'
            mac = open('/sys/class/net/%s/address' % ifname).read()
            mac = mac.rstrip('\n')

        except Exception as e:
            traceback.print_exc()
            logging.exception(e)
            error = {"status": 'error',
                     'errorText': str(e),
                     'errorCode': str(-1)}
            self.__write(error)
        else:
            self.__write({'status': 'ok', 'mac': mac})
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
            (r"/mac/([^/]+)?/?", GetMacAddressHandler),
        ]
        conf = dict(
            template_path='templates',
            static_path='static',
            debug=True,
            autoreload=True,
        )

        self.driver = None
        self.init_fiscal_driver()
        # import mock
        # self.driver = mock.Mock()

        # self.driver.cash_income(0)
        # DEBUG
        if 0:
            import mock
            self.kkm = mock.MagicMock()

        tornado.web.Application.__init__(self, handlers, **conf)

    @gen.coroutine
    def init_fiscal_driver(self):
        with (yield DRIVER_LOCK.acquire()):
            logging.debug('LOCK acquire')
            assert DRIVER_LOCK.locked()

            if self.driver:
                if self.driver.is_open_port():
                    self.driver.close_port()

            self.driver = None

            while True:
                try:
                    self.driver = driver.Driver(settings.KKM['PORT'],
                                                settings.KKM['BAUDRATE'])
                except Exception as e:
                    logging.error('init fiscal driver fail')
                    traceback.print_exc()
                    logging.exception(e)

                    logging.error('sleep 5 until next try')
                    time.sleep(5)

                else:
                    break

            # костыль против этого замеса что при первом
            # включении первая команда никогда не срабатывает
            try:
                self.driver.beep()
                self.driver.beep()
            except driver.Error as e:
                logging.warning('3десь может быть ошибка')
                traceback.print_exc()
                error_str, error_code = e.args
                logging.exception(e)

        logging.debug('LOCK release')
        assert not DRIVER_LOCK.locked()

    @gen.coroutine
    def driver_ping(self):
        with (yield DRIVER_LOCK.acquire()):
            logging.debug('LOCK acquire')
            assert DRIVER_LOCK.locked()

            is_ok = True
            try:
                self.driver.ping()
                # raise StandardError('test')
            except Exception as e:
                logging.error('ping fail')
                is_ok = False
                traceback.print_exc()
                logging.exception(e)

        logging.debug('LOCK release')
        assert not DRIVER_LOCK.locked()

        if not is_ok:
            self.init_fiscal_driver()

        # pass
        # logging.debug('haha isOpen %s', self.driver.get_state())
        # logging.debug('haha isOpen %s', self.driver.ser.isOpen())


if __name__ == "__main__":
    application = Application()
    application.listen(settings.WEB['PORT'])

    ping_cbk = tornado.ioloop.PeriodicCallback(
        application.driver_ping,
        5 * 1000,
        tornado.ioloop.IOLoop.instance()
    )
    ping_cbk.start()

    tornado.ioloop.IOLoop.instance().start()
