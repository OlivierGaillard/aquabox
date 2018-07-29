#!/usr/bin/python
import logging
from restclient import Sender
from probes import Probes
import time
import os
import logging
from log import LogUtil

logger = logging.getLogger(__name__)


class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        # TODO: checking i2c shoud not appear here
        logger.info('waiting for I2C-1 channel...')
        while not os.path.exists('/dev/i2c-1'):
            time.sleep(5.0)
        logger.info('Starting readings')
        self.ph = Probes.factory('ph')
        self.ph_value = 0.001
        self.orp = Probes.factory('orp')
        self.orp_value = 0.1
        self.temp = Probes.factory('temp')
        self.temp_value = 0.001
        logger.info('PoolMaster is initialized')
        # This script is started at reboot by cron.
        # Since the start is very early in the boot sequence we wait for the i2c-1 device

    def read_measures(self):
        logger.info("Begin readings...")
        logger.info('querying temperature')
        self.temp_value = self.temp.get_temp()
        logger.info('Temp: %s' % self.temp_value)
        logger.info('querying ORP')
        self.orp_value = self.orp.get_orp()
        logger.info('ORP: %s' % self.orp_value)
        logger.info('querying pH')
        self.ph_value = self.ph.get_ph()
        logger.info('pH: %s' % self.ph_value)
        logger.info('END readings.')

    def send_measures(self):
        logger.info('Sending measures..')
        sender = Sender()
        logger.info('orp...')
        sender.send_redox(float(self.orp_value))
        logger.info('temperature...')
        sender.send_deg(float(self.temp_value))
        logger.debug('pH...')
        sender.send_ph(float(self.ph_value))
        logger.debug('pH end.')
        logger.info('END sending.')
