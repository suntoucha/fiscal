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
from pprint import pformat


class KKMDriverHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def post(self, func_name):
        # self.add_header("Content-Type", "application/json; charset=utf-8")
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            logging.info(func_name)
            logging.info(self.request.body)

            data = json.loads(self.request.body) if self.request.body else {}

            res = yield self.application.device.exec_driver_func(
                func_name, data
            )
            logging.info('res: %s', pformat(res))

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
            if func_name == 'get_state':
                self.__write(
                    {
                        'status': 'ok',
                        'res': res
                    }
                )
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
            settings.PING_TIMEOUT * 1000,
            self.loop
        )

    def on_enter(self):
        self.ping_periodic_callback.start()
        if settings.WELCOME_MSG:
            self.device.driver.writeln(text=settings.WELCOME_MSG)
        self.device.driver.cut()

    def on_leave(self):
        self.ping_periodic_callback.stop()

    @gen.coroutine
    def ping(self):
        logging.info('ping')
        try:
            yield self.device.exec_driver_func('ping')
            # raise StandardError('test')
        except Exception as e:
            logging.error('ping fail')
            traceback.print_exc()
            logging.exception(e)

            self.loop.add_callback(
                partial(self.device.change_state, 'disconnected')
            )

    def exec_driver_func(self, func_name, params=None):
        func = None
        logging.info("func_name %s, params %s", func_name, params)

        if hasattr(self.device.driver, func_name):
            func = getattr(self.device.driver, func_name)
        else:
            raise NotImplementedError('No such method {}'.format(func_name))

        return func(**params)


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
            logging.info('try connect after %s sec', settings.CONNECT_TIMEOUT)
            self.loop.add_timeout(
                time.time() + settings.CONNECT_TIMEOUT,
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
            self.device.driver = driver.Driver(
                settings.KKM['PORT'],
                settings.KKM['BAUDRATE']
            )
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
            logging.exception(e)

        return True

    def exec_driver_func(self, func_name, params=None):
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
        self.driver_lock = toro.Lock()

        if 0:
            self.driver = mock.MagicMock()

        self.change_state('disconnected')

    @gen.coroutine
    def change_state(self, state_name):
        with (yield self.driver_lock.acquire()):
            logging.info('LOCK acquire')

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
        logging.info('LOCK release')

    @gen.coroutine
    def exec_driver_func(self, func_name, params=None):
        if not params:
            params = {}
        if self.driver_lock.locked():
            raise StandardError('DEVICE is busy')

        with (yield self.driver_lock.acquire()):
            logging.info('LOCK acquire')
            res = self.state.exec_driver_func(
                func_name, params
            )
        logging.info('LOCK release')
        raise gen.Return(res)


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
