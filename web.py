#!/usr/bin/python
# -*- coding: utf8 -*-
__author__ = 'hobbut'

from tornado import gen
import tornado.ioloop
import tornado.web
import toro
import mock
from functools import partial
# import inspect

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

            func = self.application.device.get_driver_func(func_name)

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


class ConnectedState(object):
    """docstring for ConnectedState"""
    def __init__(self, device):
        super(ConnectedState, self).__init__()
        self.device = device
        self.loop = tornado.ioloop.IOLoop.instance()

        self.ping_periodic_callback = tornado.ioloop.PeriodicCallback(
            self.ping,
            5 * 1000,
            self.loop
        )

    def on_enter(self):
        self.ping_periodic_callback.start()

    def on_leave(self):
        self.ping_periodic_callback.stop()

    def ping(self):
        logging.info('ping')
        try:
            # self.driver.ping()
            raise StandardError('test')
        except Exception as e:
            logging.error('ping fail')
            traceback.print_exc()
            logging.exception(e)

            self.loop.add_callback(
                partial(self.device.change_state, 'disconnected')
            )

    def get_driver_func(self, func_name):
        if hasattr(self.device.driver, func_name):
            func = getattr(self.device.driver, func_name)
        else:
            raise NotImplementedError('No such method {}'.format(func_name))
        return func


class DisconnectedState(object):
    def __init__(self, device):
        super(DisconnectedState, self).__init__()
        self.device = device
        self.loop = tornado.ioloop.IOLoop.instance()

    def on_enter(self):
        if self.device.driver:
            if self.device.driver.is_open_port():
                logging.info('close port: %s baudrate: %s',
                             settings.KKM['PORT'],
                             settings.KKM['BAUDRATE'])
                self.device.driver.close_port()

        self.device.driver = None

        if not self.connect():
            logging.info('try connect after 5 sec')
            self.loop.add_timeout(
                time.time() + 5,
                partial(self.device.change_state, 'disconnected')
            )
        else:
            self.loop.add_callback(
                partial(self.device.change_state, 'connected')
            )

    def connect(self):
        try:
            logging.info('try connect port: %s baudrate: %s',
                         settings.KKM['PORT'],
                         settings.KKM['BAUDRATE'])
            # self.device.driver = mock.MagicMock()
            self.device.driver = driver.Driver(settings.KKM['PORT'],
                                        settings.KKM['BAUDRATE'])
        except Exception as e:
            logging.error('init fiscal driver fail')
            traceback.print_exc()
            logging.exception(e)
            return False

        # костыль против этого замеса что при первом
        # включении первая команда никогда не срабатывает
        try:
            self.device.driver.beep()
            self.device.driver.beep()
        except driver.Error as e:
            logging.warning('3десь может быть ошибка')
            traceback.print_exc()
            error_str, error_code = e.args
            logging.exception(e)

        return True

    def get_driver_func(self, func_name):
        raise StandardError('server has no connection to fiscal')


class Device(object):
    """docstring for Device"""
    def __init__(self):
        super(Device, self).__init__()
        self.driver = None
        self.state = None
        self.transitions = {
            'connected': ConnectedState(self),
            'disconnected': DisconnectedState(self),
        }

        if 0:
            self.driver = mock.MagicMock()

        self.change_state('disconnected')

    def change_state(self, state_name):
        logging.info('-> state %s', state_name)
        if self.state:
            if hasattr(self.state, 'on_leave'):
                # logging.info('on_leave')
                self.state.on_leave()

        if state_name not in self.transitions:
            raise NotImplementedError('Error state_name %s' % state_name)

        self.state = self.transitions[state_name]

        if hasattr(self.state, 'on_enter'):
            # logging.info('on_enter')
            self.state.on_enter()

    def get_driver_func(self, func_name):
        return self.state.get_driver_func(func_name)


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

        self.device = Device()

        # self.driver = None
        # self.init_fiscal_driver()

        # import mock
        # self.driver = mock.Mock()

        # self.driver.cash_income(0)
        # DEBUG
        if 0:
            import mock
            self.kkm = mock.MagicMock()

        tornado.web.Application.__init__(self, handlers, **conf)


        # pass
        # logging.debug('haha isOpen %s', self.driver.get_state())
        # logging.debug('haha isOpen %s', self.driver.ser.isOpen())


if __name__ == "__main__":
    if 0:
        import tornado.ioloop

        loop = tornado.ioloop.IOLoop.instance()

        # def callback(*args):
        #     print 'hahah', time.time()
        #     loop.add_timeout(time.time() + 5, callback)
        # callback()
        device = Device()

        loop.start()

    if 1:
        application = Application()
        application.listen(settings.WEB['PORT'])
        tornado.ioloop.IOLoop.instance().start()
