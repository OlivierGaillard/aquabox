#!/usr/bin/python

from restclient import Sender
import logging
from box import RaspiFactory
import boxsettings

logger = logging.getLogger(__name__)


class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        if boxsettings.FAKE_DATA: # we use mockups
            logger.debug("PoolMaster init: we use mockups")
            self.raspi = RaspiFactory.getRaspi('MockupRaspi')
        else:
            logger.debug("PoolMaster init: we use real probes and real pi")
            self.raspi = RaspiFactory.getRaspi('Raspi')

        logger.debug('PoolMaster is initialized')
        self.readings_done = False
        self.sendings_done = False

    def read_measures(self):
        logger.debug("Begin readings...")

        logger.debug('querying temperature')
        self.temp_value = self.raspi.get_temp_from_pi()
        logger.debug('Temp: %s' % self.temp_value)

        logger.debug('querying ORP')
        self.orp_value = self.raspi.get_orp_from_pi()
        logger.debug('ORP: %s' % self.orp_value)

        logger.debug('querying pH 3 times')
        max_tries_ph = 3
        ph_values = []
        for i in range(0, max_tries_ph):
            ph = self.raspi.get_ph_from_pi()
            logger.debug('%s. pH = %s' % (i+1, ph))
            if ph <= 2:
                logger.warning('we do not value <= 2')
            else:
                ph_values.append(ph)
        if len(ph_values) > 0:
            self.ph_value = sum(ph_values) / len(ph_values)
            logger.debug('Middle value of pH: %s' % self.ph_value)
        else:
            self.ph_value = 0
            logger.warning('We was not able to read a valid pH value. Sending default one: %s' % 0)
        logger.debug('END readings.')
        self.readings_done = True


    def send_measures(self):
        logger.info('Sending measures..')
        redox_sent = ph_sent = temp_sent = False
        sender = Sender()
        logger.debug('orp...')
        try:
            sender.send_redox(float(self.orp_value))
            redox_sent = True
        except:
            logger.warning('We was not able to send redox to REST')
        logger.debug('temperature...')
        try:
            sender.send_deg(float(self.temp_value))
            temp_sent = True
        except:
            logger.warning('We was not able to send deg to REST')

        logger.debug('pH...')
        try:
            sender.send_ph(float(self.ph_value))
            ph_sent = True
        except:
            logger.warning('We was not able to send pH to REST')

        self.sendings_done = redox_sent and ph_sent and temp_sent
        if self.sendings_done:
            logger.info('All measures sent.')
        else:
            logger.warning('Some measures fail to be sent.')
