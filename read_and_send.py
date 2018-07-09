#!/usr/bin/python
import logging
from restclient import Sender
import boxsettings
import sleep
import random
from probes import Probes

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.DEBUG)



class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        self.ph = Probes.factory('ph')
        self.orp = Probes.factory('orp')
        self.temp = Probes.factory('temp')

    def read_measures(self):
        logging.debug("Begin readings...")
        logging.debug('querying temperature')
        self.temp_value = self.temp.get_temp()
        logging.debug('Temp: %s' % self.temp_value)
        logging.debug('querying ORP')
        self.orp_value = self.orp.get_orp()
        logging.debug('ORP: %s' % self.orp_value)
        logging.debug('querying pH')
        self.ph_value = self.ph.get_ph()
        logging.debug('pH: %s' % self.ph_value)
        logging.debug('END readings.')

    def send_measures(self):
        logging.debug('Sending measures..')
        sender = Sender()
        sender.send_redox(self.orp_value)
        sender.send_deg(self.temp_value)
        sender.send_ph(self.ph_value)
        logging.debug('END sending.')




def main():
    poolMaster = PoolMaster()
    poolMaster.read_measures()
    #poolMaster.send_measures()

if __name__ == '__main__':
    main()
