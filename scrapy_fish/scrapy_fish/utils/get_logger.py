#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: get_logger.py 
@time: 2019/04/25
@desc: 

"""

# coding: utf-8

import os
import logging
import logging.handlers


def get_logger(name, level=logging.DEBUG, file=True, log_dir=''):
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    formats = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(threadName)s - %(message)s')

    if file:
        if not log_dir:
            log_dir = os.path.abspath(
                os.path.dirname(__file__) + os.path.sep + "./" + 'logs')
        log_dir = os.path.expanduser(log_dir)
        if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, '{}.log'.format(name.replace('.py', ''))), when='D', encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formats)
        _logger.addHandler(file_handler)

    stream_headler = logging.StreamHandler()
    stream_headler.setLevel(level)
    stream_headler.setFormatter(formats)
    _logger.addHandler(stream_headler)

    return _logger


if __name__ == '__main__':
    log = get_logger(name=__name__, file=False)
    log.debug('debug')
    log.info('info')
    log.warning('warning')
    log.error('error')
