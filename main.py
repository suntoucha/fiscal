# -*- coding: utf-8 -*-
# from pprint import pprint as pp
# import json
import copy
import time
import settings
from functools import partial

import tornado.ioloop
import tornado.web
from tornado.escape import json_decode

from log import log
import sign
####### from log import setup_log
# import logging as log

from cloud import Cloud
from sock_connection import SockjsConnection
from sock_connection import SocketRouter

from tornado.options import define, options
from pprint import pprint as pp


define("port", default=8000, help="run on the given port", type=int)
define("config", default='config.json', help="JSON config file", type=str)

from rpc import Rpc


class IndexHandler(tornado.web.RequestHandler):
    """Template renderer"""

    def get(self, *args, **kwargs):
        self.render('index.html')


def debugdebugdebug():
    # return
    import pdb
    import ipdb
    # import pudb
    # import random
    import objgraph

    # objgraph.show_growth()
    # pdb.set_trace()
    import gc
    gc.collect()
    print '''len(objgraph.by_type('SockjsConnection')) = ''', len(objgraph.by_type('SockjsConnection'))
    print '''len(objgraph.by_type('Cloud')) = ''', len(objgraph.by_type('Cloud'))
    print '''len(objgraph.by_type('Rpc')) = ''', len(objgraph.by_type('Rpc'))
    print '''len(objgraph.by_type('Connection')) = ''', len(objgraph.by_type('Connection'))
    print '''len(objgraph.by_type('Client')) = ''', len(objgraph.by_type('Client'))
    # cloud_list = objgraph.by_type('Cloud')
    # sock_list = objgraph.by_type('SockjsConnection')
    # rpc_list = objgraph.by_type('Rpc')
    # cloud = random.choice(cloud_list)
    # sock = random.choice(sock_list)
    # rpc = random.choice(rpc_list)

    # return
    log.info('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    collected = gc.collect()
    log.info("Garbage collector: collected %d objects." % (collected))
    log.info('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    h = hp.heap()
    log.info(h)

    ipdb.set_trace()
    # pdb.set_trace()
    


    # pudb.set_trace()
    return


class DebugHandler(tornado.web.RequestHandler):
    """Template renderer"""

    def get(self, *args, **kwargs):
        debugdebugdebug()
        self.write('debugdebug debug')

import gc
import resource
from guppy import hpy
hp = hpy()
hp.setrelheap()

def collect():
    # return
    import objgraph
    """
import objgraph
import inspect
len(objgraph.by_type('Connection'))
# objgraph.show_backrefs(objgraph.by_type('Cloud')[3])

    """
    if 0:
        log.info('''len(objgraph.by_type('SockjsConnection')) = %s''' % len(objgraph.by_type('SockjsConnection')))
        log.info('''len(objgraph.by_type('Cloud')) = %s''' % len(objgraph.by_type('Cloud')))
        log.info('''len(objgraph.by_type('Rpc')) = %s''' % len(objgraph.by_type('Rpc')))
        log.info('''len(objgraph.by_type('Connection')) = %s''' % len(objgraph.by_type('Connection')))
        log.info('''len(objgraph.by_type('Client')) = %s''' % len(objgraph.by_type('Client')))
        log.info('''len(objgraph.by_type('Task')) = %s''' % len(objgraph.by_type('Task')))
        log.info('''len(objgraph.by_type('Runner')) = %s ''' % len(objgraph.by_type('Task')))
        log.info('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    collected = gc.collect()
    log.info("Garbage collector: collected %d objects." % (collected))
    log.info('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # log.info('''len(objgraph.by_type('Connection')) = %s''' % len(objgraph.by_type('Connection')))
    # это тоже не надо оч протормаживает просто 
    # h = hp.heap()
    # log.info(h)
    # log.info(_.more)


class EventHandler(tornado.web.RequestHandler):

    def post(self, channel, event):
        """
            Миша,
            внедрил передачу параметра auth_signature, он уже должен начать тебе приходить

            Генерируется следующим образом:
            $query = "send_timestamp=" . time() . "&data_md5=" . md5( $payload_encoded );
            $auth_signature = hash_hmac( 'sha256', $query, 'a26927b6da90e8e1fa15', false );
            $signed_query = $query . "&auth_signature=" . $auth_signature;
        """
        content_type = self.request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            self.arguments = json_decode(self.request.body)

        log.info('EVENT %s %s' % (channel, event))
        log.info('EVENT JSON: %s' % self.request.body)

        log.info('QUERY: %s' % self.request.query)
        log.info('PATH: %s' % self.request.path)
        log.info('BODY: %s' % self.request.body)

        try:
            log.info('--------------')
            is_ok = sign.check_sign(self.request.query, self.request.body)
            log.info('Auth res = %s' % is_ok)
            if not is_ok:
                self.set_status(401)

            else:
                Rpc.publish(self.application.cloud,
                            channel,
                            event,
                            self.request.body)
                self.set_status(200)
            log.info('--------------')
        except Exception, e:
            log.error(repr(e))


class Application(tornado.web.Application):
    def __init__(self):

        handlers = [
            (r'/', IndexHandler),
            # (r'/debug', DebugHandler),
            (r"/channel/([^/]+)/event/([^/]+)/", EventHandler),
        ]

        handlers += SocketRouter.urls

        conf = dict(
            template_path='templates',
            static_path='static',
            # debug=True,
            autoreload=True,
        )

        SockjsConnection.application = self

        self.config = {
            "proxy_for_publish": [
            ],
            "proxy_for_subscribe": [
            ]
        }

        self.cloud = Cloud()

        from zoo import ZooTornado
        self.zoo = ZooTornado(options.port,
                              server=settings.ZOOKEEPER_URL,
                              on_config_change=self.on_config_change)
        self.zoo.set_node()

        tornado.web.Application.__init__(self, handlers, **conf)

        self.already_subscribe_to = None
        self.already_publish_to = None

    def on_config_change(self, sub_proxy, pub_proxy):
        tornado.ioloop.IOLoop.instance().add_callback(partial(self.connect_cloud, sub_proxy, pub_proxy))

    def connect_cloud(self, sub_proxy, pub_proxy):

        print '-' * 40
        pp((self.get_proxy_for_subscribe(sub_proxy),
            self.get_proxy_for_publish(pub_proxy)))
        print '-' * 40

        self.config['proxy_for_publish'] = self.get_proxy_for_publish(pub_proxy)
        self.config['proxy_for_subscribe'] = self.get_proxy_for_subscribe(sub_proxy)

        pp(SockjsConnection.participants)

        pp('Change sub connection')
        self.re_publish_cloud(copy.deepcopy(self.config))

        if self.already_publish_to and self.already_publish_to == self.config['proxy_for_publish']:
            pass
        else:
            log.info('Republish after 12 sec')
            tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 12,
                                                         partial(self.re_publish_cloud,
                                                                 copy.deepcopy(self.config)))

        log.info('Resubscribe after 12 sec')
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 12,
                                                     partial(self.re_subscribe_cloud,
                                                             SockjsConnection.participants,
                                                             copy.deepcopy(self.config)))


        pp(self.config['proxy_for_subscribe'])
        pp(self.config['proxy_for_publish'])

    def re_subscribe_cloud(self, participants, config):
        if config['proxy_for_subscribe'] == self.config['proxy_for_subscribe']:
            log.warn('Ok reconnect.')
        else:
            log.warn('Old config.')
            return

        if self.already_subscribe_to and self.already_subscribe_to == self.config['proxy_for_subscribe']:
            log.warn('Already Subscribe to %s' % self.already_subscribe_to)
            return

        for sock in participants:
            sock.cloud.set_recv_cb(sock.on_receive_message_from_cloud)
            sock.cloud.connect_sub(self.config['proxy_for_subscribe'])

        self.already_subscribe_to = copy.deepcopy(
            self.config['proxy_for_subscribe']
        )

    def re_publish_cloud(self, config):
        if self.already_publish_to and self.already_publish_to == self.config['proxy_for_publish']:
            log.warn('Already publish to %s' % self.already_publish_to)
            return

        if config['proxy_for_publish'] == self.config['proxy_for_publish']:
            log.warn('Ok reconnect.')
        else:
            log.warn('Old config.')
            return

        log.info('ALREADY PUBLISHED TO %s' % self.already_publish_to)
        log.info('PUBLISH TO           %s' % self.config['proxy_for_publish'])

        self.cloud.close_pub()
        self.cloud.connect_pub(self.config['proxy_for_publish'])

        self.already_publish_to = copy.deepcopy(self.config['proxy_for_publish'])
        log.info('PUBLISHED TO %s' % self.already_publish_to)

    # TODO этот говнокод надо бы переписать во что товроде convert_from_zoo_format
    def get_proxy_for_publish(self, proxies):
        proxy_for_publish = [
            {
                key: proxy[key] for key in ['host', 'port']
            }
            for proxy in proxies.values()
        ]
        return proxy_for_publish

    def get_proxy_for_subscribe(self, proxy):
        proxy_for_subscribe = [
            {
                key: proxy[key] for key in ['host', 'port']
            }
        ]
        return proxy_for_subscribe


import resource
import psutil
import os
def resource_stat():
    p = psutil.Process(os.getpid())
    log.info('*******************')
    log.info(p.get_open_files())
    pp(p.get_connections())
    pp(len(p.get_connections()))

    for name, desc in [('RLIMIT_CORE', 'core file size'),
                       ('RLIMIT_CPU',  'CPU time'),
                       ('RLIMIT_FSIZE', 'file size'),
                       ('RLIMIT_DATA', 'heap size'),
                       ('RLIMIT_STACK', 'stack size'),
                       ('RLIMIT_RSS', 'resident set size'),
                       ('RLIMIT_NPROC', 'number of processes'),
                       ('RLIMIT_NOFILE', 'number of open files'),
                       ('RLIMIT_MEMLOCK', 'lockable memory address'),
                       ]:
        limit_num = getattr(resource, name)
        soft, hard = resource.getrlimit(limit_num)
        log.info('Maximum %-25s (%-15s) : %20s %20s' % (desc, name, soft, hard))
    log.info('*******************')




if __name__ == '__main__':

    tornado.options.parse_command_line()

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    print 'Soft, Hard limit starts as  :', (soft, hard)
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE,
                           (settings.CONNECTION_LIMIT,
                            settings.CONNECTION_LIMIT))

        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        print 'Soft, Hard limit changed to :', (soft, hard)
    except ValueError, e:
        for i in range(100):
            log.error('!!!!! Cant set NOFILE limit to %d %s current limit %d, %d' % (settings.CONNECTION_LIMIT, e, hard, soft))
        raise e

    app = Application()
    app.listen(options.port)

    # g_collect = tornado.ioloop.PeriodicCallback(collect, 6000)
    g_collect = tornado.ioloop.PeriodicCallback(collect, 60000)
    g_collect.start()

    resource_stat()
    # g_resource_stat = tornado.ioloop.PeriodicCallback(resource_stat, 30000)
    # g_resource_stat.start()

    ioloop_instance = tornado.ioloop.IOLoop.instance()
    try:
        ioloop_instance.start()
    finally:
        app.cloud.close_pub()
        # app.cloud.term()
