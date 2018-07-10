#!/usr/bin/python
import logging
from restclient import Sender
import boxsettings
import sleep
import random
from probes import Probes

class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        self.ph = Probes.factory('ph')
        self.ph_value = 0.001
        self.orp = Probes.factory('orp')
        self.orp_value = 0.1
        self.temp = Probes.factory('temp')
        self.temp_value = 0.001

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
        logging.info('sent.')
        logging.info('temp...')
        sender.send_deg(float(self.temp_value))
        logging.info('sent.')
        logging.info('pH...')
        sender.send_ph(float(self.ph_value))
        logging.info('sent.')
        logging.debug('END sending.')




def main():
    logname = '/home/pi/phweb/box/rest.log'
    logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='a', level=logging.DEBUG)
    logging.info('info test')
    poolMaster = PoolMaster()
    poolMaster.read_measures()
    poolMaster.send_measures()

if __name__ == '__main__':
    main()
