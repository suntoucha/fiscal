#!/usr/bin/python
# -*- coding: utf8 -*-
import settings
import logging
import kkmdrv

kkm = None


def hello(name='zzzz', address=''):
    logging.info(name)
    logging.info(address)

def postJson(self, **argv):
    if data.get("close"):
        self.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
    else:
        self.kkm.reportWoClose(kkmdrv.DEFAULT_ADM_PASSWORD)
    self.success()


def print_report(self, close=None):
    if close:
        self.kkm.reportWClose(kkmdrv.DEFAULT_ADM_PASSWORD)
    else:
        self.kkm.reportWoClose(kkmdrv.DEFAULT_ADM_PASSWORD)
