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
        subprocess.call(["git", "pull"])
        logger.info('Update done')
    else:
        logger.info('We do NOT make a git pull')

def take_measures(raspi, pool_settings, logger):
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
        poolMaster = PoolMaster(raspi=raspi)
        poolMaster.read_measures()
        poolMaster.send_measures()
        logger.info('End of JOB')
    else:
        logger.info('We do not take readings.')

def send_battery_charge_level(raspi, pool_settings, logger):
    try:
        sender = Sender()
        battery_level = raspi.get_charge_level()
        logger.info('Battery charge in percent: %s' % battery_level)
        if ONLINE:
            logger.info('Sending info to REST')
            response = sender.send_battery_level(battery_level)
            logger.info('Answer: %s' % response.status_code)
        else:
            logger.info(('Off-line. Battery level not sent'))
    except:
        logger.fatal("Cannot create pijuice object")



def main(pool_settings, logger):
    time.sleep(30)  # to wait for network goes up
    do_update(pool_settings, logger)
    logger.debug('Initialising raspi...')
    raspi = None
    try:
        if boxsettings.FAKE_DATA:
            logger.info('Creating a Mock-Raspi..')
            raspi = RaspiFactory.getRaspi('mock')
        else:
            logger.info('Creating a real Raspi..')
            raspi = RaspiFactory.getRaspi('Raspi')
    except Exception, e:
        logger.fatal('Fail to init raspi', exc_info=True)
        if pool_settings.enable_shutdown():
            logger.info('doing shutdown, as planned')
            raspi.shutdown()
        else:
            logger.fatal('No shutdown, as planned')
    logger.info('Raspi initialised.')
    if SHUTDOWN:
        logger.info('Shutdown of pijuice and pi. Alarms disabled...')
        logger.debug('Sending log..')
        raspi.send_log()
        logger.debug('done.')
        raspi.bigshutdown()
        exit(0)
    logger.info('Taking measures..')
    take_measures(raspi, pool_settings, logger)
    logger.info('Measures taken')
    logger.info('Sending charge level..')
    send_battery_charge_level(raspi, pool_settings, logger)
    logger.info('Charge level sent')
    logger.info('Setting wakeup..')
    raspi.setup_wakeup()
    logger.info('Wakeup set')
    logger.debug('sending log...')
    raspi.send_log()
    logger.debug('done')

    if pool_settings.enable_shutdown():
        logger.info('Shutdown is enabled. Starting shutdown..')
        raspi.shutdown() ## logs are sent too
    else:
        logger.info('Shutdown disabled. End of job')


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

    # create a permanent file logger with rotate
    current_dir = os.path.abspath('.')
    main_log = os.path.join(current_dir, 'mainlog.log')
    fh2 = logging.FileHandler(main_log)
    fh2 = RotatingFileHandler(main_log, maxBytes=10485760, backupCount=10)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    fh.setFormatter(formatter)
    fh2.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.addHandler(fh)
    logger.addHandler(fh2)

    logger.debug('logger set to log level %s' % log_level)
    logger.debug('permanent log file: %s' % main_log)
    logger.info('Poolsettings:')
    READING = pool_settings.enable_reading()
    logger.info('Readings: %s' % READING)
    ONLINE = pool_settings.is_online()
    logger.info('ONLINE: %s' % ONLINE)
    SHUTDOWN = pool_settings.bigshutdown()
    logger.info('BIG Shutdown planed? %s' % SHUTDOWN)
    main(pool_settings, logger)




