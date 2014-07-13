# -*- encoding: utf-8 -*-

# import os
# import sys
import logging
import logging.config

from os.path import join, dirname, abspath
import config

config = config.from_yaml(
    join(dirname(abspath(__file__)), 'config.yaml')
)

globals().update(config)
log_cfg = config.get("LOG_CFG")
if log_cfg:
    logging.config.dictConfig(log_cfg)
