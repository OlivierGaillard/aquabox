from __future__ import print_function
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from restclient import Sender
import time
from poolsettings import PoolSettings
from read_and_send import PoolMaster
import boxsettings
from box import RaspiFactory
from log import LogUtil
import os

ONLINE = False  # Are we online?
READING = False # Do we take measures?
SHUTDOWN = False # No readings, alarms off and desactivated, pijuice off, raspi off

def do_update(pool_settings, logger):
    # Checking if an update is required
    if pool_settings.do_update() and pool_settings.is_online():
        logger.info('We will make a git pull')
    else:
        logger.info('We do NOT make a git pull')

def take_measures(pool_settings, logger):
    if ONLINE:
        logger.debug('take_measures: We are online')
    else:
        logger.debug('take_measures: We are NOT online')
    if READING:
        logger.debug('readings are enabled')
    else:
        logger.debug('readings are disabled')
    if READING and ONLINE:
        logger.info('We will make reading')
    else:
        logger.info('We do not take readings.')
    logger.debug('take_measures: pool_settings')
    logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))

def send_battery_charge_level(pool_settings, logger):
    try:
        sender = Sender()
        logger.info('Sender online: %s' % sender.is_online())
        if ONLINE:
            logger.info('ONLINE')
        else:
            logger.info(('Off-line. Battery level not sent'))
        logger.debug('take_measures: pool_settings')
        logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))
    except:
        logger.fatal("Cannot create pijuice object")



def main(pool_settings, logger):
    do_update(pool_settings, logger)
    take_measures(pool_settings, logger)
    send_battery_charge_level(pool_settings, logger)
    logger.debug('pool_settings: shutdown: %s' % pool_settings.enable_shutdown())


if __name__ == '__main__':
    logname = boxsettings.LOG_FILE
    pool_settings = PoolSettings()
    log_util = LogUtil()
    log_level = log_util.get_log_level(pool_settings.log_level())
    # create logger at the root level. Otherwise the loggers in module will not use this configuration.
    logger = logging.getLogger()
    logger.setLevel(log_level)


    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logname, mode='w')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.addHandler(fh)
    logger.debug('logger set to log level %s' % log_level)
    logger.info('Poolsettings:')
    READING = pool_settings.enable_reading()
    logger.info('Readings: %s' % READING)
    ONLINE = pool_settings.is_online()
    logger.info('ONLINE: %s' % ONLINE)
    SHUTDOWN = pool_settings.bigshutdown()
    logger.info('BIG Shutdown planed? %s' % SHUTDOWN)
    main(pool_settings, logger)




