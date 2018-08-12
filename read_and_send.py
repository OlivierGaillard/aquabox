#!/usr/bin/python

from restclient import Sender
import logging
import boxsettings

class PoolMaster:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self, raspi):
        self.raspi = raspi
        self.logger = logging.getLogger('PoolMaster')
        self.readings_done = False
        self.sendings_done = False
        self.logger.debug('PoolMaster is initialized')

    def read_measures(self):
        self.logger.debug("Begin readings...")
        self.logger.debug('querying temperature')
        self.temp_value = self.raspi.get_temp_from_pi()
        self.logger.debug('Temp: %s' % self.temp_value)

        self.logger.debug('querying ORP')
        self.orp_value = self.raspi.get_orp_from_pi()
        self.logger.debug('ORP: %s' % self.orp_value)

        self.logger.debug('querying pH 3 times')
        max_tries_ph = 3
        ph_values = []
        for i in range(0, max_tries_ph):
            ph = self.raspi.get_ph_from_pi()
            self.logger.debug('%s. pH = %s' % (i+1, ph))
            if ph <= 2:
                self.logger.warning('we do not value <= 2')
            else:
                ph_values.append(float(ph))
        if len(ph_values) > 0:
            self.ph_value = sum(ph_values) / len(ph_values)
            self.logger.debug('Middle value of pH: %s' % self.ph_value)
        else:
            self.ph_value = 0
            self.logger.warning('We was not able to read a valid pH value. Sending default one: %s' % 0)
        self.logger.debug('END readings.')
        self.readings_done = True


    def send_measures(self):
        self.logger.info('Sending measures..')
        redox_sent = ph_sent = temp_sent = False
        sender = Sender()
        self.logger.debug('orp...')
        try:
            sender.send_redox(float(self.orp_value))
            redox_sent = True
        except Exception, e:
            self.logger.warning('We was not able to send redox to REST', exc_info=True)
        self.logger.debug('temperature...')
        try:
            sender.send_deg(float(self.temp_value))
            temp_sent = True
        except Exception, e:
            self.logger.warning('We was not able to send deg to REST', exc_info=True)

        self.logger.debug('pH...')
        try:
            sender.send_ph(float(self.ph_value))
            ph_sent = True
        except Exception, e:
            self.logger.warning('We was not able to send pH to REST', exc_info=True)

        self.sendings_done = redox_sent and ph_sent and temp_sent
        if self.sendings_done:
            self.logger.info('All measures sent.')
        else:
            self.logger.warning('Some measures fail to be sent.')
