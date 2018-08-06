import boxsettings
import logging
import time
from abc import ABCMeta, abstractmethod
import os
from probes import Probes

logger = logging.getLogger(__name__)


class RaspiFactory:
    """A factory to create a real or a mockup Raspberry Pi"""
    __metaclass__ = ABCMeta

    # all probes are initialised by method 'initSensors' of the concrete classes
    temp_probe = None
    ph_probe   = None
    orp_probe  = None
    ph_value = 0.001
    orp_value = 0.1
    temp_value = 0.001

    def __init__(self):
        self.initSensors()

    @staticmethod
    def getRaspi(name):
        if name == 'Raspi':
            raspi = Raspi()
            logger.debug('made a real raspi')
            return raspi
        else:
            logger.debug('RaspiFactory: will create one MockRaspi')
            raspi = MockRaspi()
            logger.debug('made a mock raspi')
            return raspi


    @abstractmethod
    def initSensors(self):
        pass


    def get_temp_from_pi(self):
        self.temp_value = self.temp_probe.get_temp()
        return self.temp_value

    def get_ph_from_pi(self):
        self.ph_value = self.ph_probe.get_ph()
        return  self.ph_value

    def get_orp_from_pi(self):
        self.orp_value = self.orp_probe.get_orp()
        return self.orp_value

    @abstractmethod
    def get_charge_level(self):
        pass


class MockRaspi(RaspiFactory):
    "A mockup Raspberry pi"
    name = "MockupRaspi"

    def initSensors(self):
        self.ph_probe   = Probes.factory('mock_ph')
        self.orp_probe  = Probes.factory('mock_orp')
        self.temp_probe = Probes.factory('mock_temp')
        logger.debug('MockRaspi initSensors done')


    def get_charge_level(self):
        return 60;

class Raspi(RaspiFactory):
    "A real raspberry pi 3 with pijuice and sensors plate"
    name = "Raspi-3"


    def initSensors(self):
        logger.debug('waiting for I2C-1 channel...')
        while not os.path.exists('/dev/i2c'):
            time.sleep(5.0)
        self.ph_probe   = Probes.factory('ph')
        self.orp_probe  = Probes.factory('orp')
        self.temp_probe = Probes.factory('temp')
        logger.debug('Raspi-3 initSensors DONE')


    def get_charge_level(self):
        import pijuice
        pj = pijuice.PiJuice(1, 0x14)
        charge = pj.status.GetChargeLevel()
        battery_level = charge['data']
        return battery_level







