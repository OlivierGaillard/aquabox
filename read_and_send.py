#!/usr/bin/python
import logging
from restclient import Sender
from probes import Probes
import time
import os

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='a',
                    level=logging.DEBUG)


class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        # TODO: checking i2c shoud not appear here
        logging.info('waiting for I2C-1 channel...')
        while not os.path.exists('/dev/i2c-1'):
            time.sleep(5.0)
        logging.info('Starting readings')
        self.ph = Probes.factory('ph')
        self.ph_value = 0.001
        self.orp = Probes.factory('orp')
        self.orp_value = 0.1
        self.temp = Probes.factory('temp')
        self.temp_value = 0.001
        logging.info('PoolMaster is initialized')
        # This script is started at reboot by cron.
        # Since the start is very early in the boot sequence we wait for the i2c-1 device

    def read_measures(self):
        logging.info("Begin readings...")
        logging.info('querying temperature')
        self.temp_value = self.temp.get_temp()
        logging.info('Temp: %s' % self.temp_value)
        logging.info('querying ORP')
        self.orp_value = self.orp.get_orp()
        logging.info('ORP: %s' % self.orp_value)
        logging.info('querying pH')
        self.ph_value = self.ph.get_ph()
        logging.info('pH: %s' % self.ph_value)
        logging.info('END readings.')

    def send_measures(self):
        logging.info('Sending measures..')
        sender = Sender()
        logging.info('orp...')
        sender.send_redox(float(self.orp_value))
        logging.info('temperature...')
        sender.send_deg(float(self.temp_value))
        logging.info('pH...')
        sender.send_ph(float(self.ph_value))
        logging.debug('END sending.')
