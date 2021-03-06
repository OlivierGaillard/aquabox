from __future__ import print_function
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from restclient import Sender
import time
import datetime
from poolsettings import PoolSettings
from read_and_send import PoolMaster
import boxsettings
from box import RaspiFactory
import os
from log import LogUtil

ONLINE = False  # Are we online?
READING = False # Do we take measures?
BIGSHUTDOWN = False # No readings, alarms off and desactivated, pijuice off, raspi off
UPDATE = True

def do_update(pool_settings, logger):
    # Checking if an update is required
    logger.debug('do_update: pool_settings')
    logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))
    logger.debug('do_update pool_settings. do_update? %s ' % pool_settings.do_update())
    if pool_settings.do_update() and pool_settings.is_online():
        logger.info('We will make a git pull')
        subprocess.call(["git", "pull"])
        logger.info('Update done')
    else:
        logger.info('We do NOT make a git pull')


def take_measures(raspi, pool_settings, logger):
    logger.debug('take_measures: pool_settings')
    logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))
    logger.debug('do_update pool_settings. do_update? %s ' % pool_settings.do_update())

    if ONLINE:
        logger.debug('take_measures: We are ONLINE')
    else:
        logger.debug('take_measures: We are NOT ONLINE')
    if READING:
        logger.debug('READING is enabled')
    else:
        logger.debug('READING is disabled')
    if READING and ONLINE:
        logger.info('We will make reading')
        poolMaster = PoolMaster(raspi=raspi)
        poolMaster.read_measures()
        poolMaster.send_measures()
        logger.info('End of JOB')
    else:
        logger.info('We do not take readings.')

    logger.debug('AFTER measures are taken: pool_settings')
    logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))
    logger.debug('do_update pool_settings. do_update? %s ' % pool_settings.do_update())


def send_battery_charge_level(raspi, pool_settings, logger):
    logger.debug('send_battery_charge_level: pool_settings')
    logger.debug('Online: %s Reading: %s' % (pool_settings.is_online(), pool_settings.enable_reading()))
    logger.debug('do_update pool_settings. do_update? %s ' % pool_settings.do_update())

    try:
        sender = Sender()
        battery_level = raspi.get_charge_level()
        logger.info('Battery charge in percent: %s' % battery_level)
        if ONLINE:
            logger.info('ONLINE: Sending info to REST')
            response = sender.send_battery_level(battery_level)
            logger.info('Answer: %s' % response.status_code)
        else:
            logger.info(('NOT ONLINE. Battery level not sent'))
    except:
        logger.fatal("Cannot create pijuice object")



def main(pool_settings, logger):
    do_update(pool_settings, logger)
    logger.debug('Initialising raspi...')
    raspi = None
    try:
        if boxsettings.FAKE_DATA:
            logger.info('Creating a Mock-Raspi..')
            raspi = RaspiFactory.getRaspi(pool_settings, 'mock')
        else:
            logger.info('Creating a real Raspi..')
            raspi = RaspiFactory.getRaspi(pool_settings, 'Raspi')
    except Exception, e:
        logger.fatal('Fail to init raspi', exc_info=True)
        if pool_settings.enable_shutdown() or BIGSHUTDOWN:
            logger.info('doing shutdown, as planned')
            raspi.shutdown()
        else:
            logger.fatal('No shutdown, as planned')
    logger.info('Raspi initialised.')
    if BIGSHUTDOWN:
        logger.info('Shutdown of pijuice and pi. Alarms disabled...')
        logger.debug('Sending log..')
        raspi.send_log()
        logger.debug('done.')
        raspi.bigshutdown()
        exit(0)
    if ONLINE == False:
        logger.info('We are not online. Then we shutdown in 5 minutes')
        # then how to shutdown in 5 minutes? shutdown -h +300
        # stop shutdown with: shutdown -c
        raspi.shutdown_later(5)
        # os.system('shutdown -h +5')
        # os._exit(0)
    logger.info('Taking measures..')
    take_measures(raspi, pool_settings, logger)
    logger.info('Measures taken')
    logger.info('Sending charge level..')
    send_battery_charge_level(raspi, pool_settings, logger)
    logger.info('Charge level sent')
    logger.info('Setting wakeup..')
    raspi.setup_wakeup()
    logger.info('Wakeup set')

    if pool_settings.enable_shutdown():
        logger.info('Sending log...')
        raspi.send_log()
        logger.info('Done.')
        logger.info('(pool_settings: Shutdown is enabled. Starting shutdown..')
        raspi.shutdown()
    else:
        logger.info('pool_settings: Shutdown disabled.')






def ping_rest(logger):
    host = 'aquawatch.ch'
    online = False
    maxtries = 30
    count = 0
    logger.debug('ping_rest...')
    while online == False and count < maxtries:
        logger.debug('.')
        rep = os.system('ping -c 1 %s' % host )
        if rep == 0:
            online = True
        time.sleep(3)
        count += 1
    logger.debug('ping end. Online: %s' % online)
    return online

if __name__ == '__main__':
    logname = boxsettings.LOG_FILE


    # create logger at the root level. Otherwise the loggers in module will not use this configuration.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)


    # create a permanent file logger with rotate
    current_dir = os.path.abspath('.')
    main_log = os.path.join(current_dir, 'mainlog.log')
    fh2 = logging.FileHandler(main_log)
    fh2 = RotatingFileHandler(main_log, maxBytes=10485760, backupCount=10)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)


    fh2.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


    logger.addHandler(fh2)
    logger.debug('removing old rest.log file...')
    try:
        os.unlink(logname)
    except Exception, e:
        logger.debug('failed to remove file', exc_info=True)

    fh = logging.FileHandler(logname)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)


    logger.addHandler(fh)
    logger.debug('Waiting until network goes up...')
    ONLINE = ping_rest(logger)

    logger.info('Setting time..')
    try:
        subprocess.call(["sudo", "hwclock", "--hctosys"])
        txt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' -- Started\n'
        logger.info(txt)
        logger.info('Time set')
    except Exception, e:
        logger.warning('Problem to set the time:', exc_info=True)

    logger.debug('Create now the PoolSettings instance..')
    pool_settings = PoolSettings()
    logger.setLevel(pool_settings.log_level())
    log_util = LogUtil()
    log_level = log_util.get_log_level(pool_settings.log_level())
    logger.debug('logger set to log level %s' % log_level)
    logger.debug('permanent log file: %s' % main_log)
    logger.info('Poolsettings:')
    UPDATE = pool_settings.do_update()
    logger.info('UPDATE: %s' % UPDATE)
    READING = pool_settings.enable_reading()
    logger.info('Readings: %s' % READING)
    ONLINE = pool_settings.is_online()
    logger.info('ONLINE: %s' % ONLINE)
    BIGSHUTDOWN = pool_settings.bigshutdown()
    logger.info('BIG Shutdown planed? %s' % BIGSHUTDOWN)
    main(pool_settings, logger)
