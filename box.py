import logging
import time, datetime
from abc import ABCMeta, abstractmethod
import os
from probes import Probes
import subprocess
from poolsettings import PoolSettings
from shutdown import WakeUp
from log import LogUtil
from restclient import Sender
import boxsettings

class RaspiFactory:
    """A factory to create a real or a mockup Raspberry Pi"""
    __metaclass__ = ABCMeta

    # all probes are initialised by method 'initSensors' of the concrete classes
    temp_probe = None
    ph_probe   = None
    orp_probe  = None
    #pj         = None # Pijuice
    ph_value = 0.001
    orp_value = 0.1
    temp_value = 0.001

    pool_settings = None
    wake_up = None

    def __init__(self, pool_settings):
        self.logger = logging.getLogger('RaspiFactory')
        self.logger.debug('RaspiFactory: __init__')
        self.pool_settings = pool_settings
        self.initSensors()
        self.wake_up = WakeUp(self.pool_settings)
        self.logger = logging.getLogger('RaspiFactory')

    @staticmethod
    def getRaspi(pool_settings, name):

        logger = logging.getLogger('static:getRaspi')
        if name == 'Raspi':
            raspi = Raspi(pool_settings)
            logger.debug('making a real raspi...')
            raspi.initPijuice()
            raspi.connect_pijuice()
            logger.debug('Real raspi ready.')
            return raspi
        else:
            logger.debug('RaspiFactory: will create one MockRaspi')
            raspi = MockRaspi(pool_settings)
            raspi.initPijuice()
            raspi.connect_pijuice()
            logger.debug('Mock raspi ready')
            return raspi

    @abstractmethod
    def initPijuice(self):
        pass

    @abstractmethod
    def connect_pijuice(self):
        pass

    @abstractmethod
    def initSensors(self):
        pass


    def get_temp_from_pi(self):
        self.logger.debug('get_temp_from_pi')
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

    @abstractmethod
    def setup_wakeup(self):
        pass

    def save_log(self):
        pass

    def send_log(self):
        self.logger.info('Sending log file')
        try:
            sender = Sender()
            self.logger.info('Bye bye.')
            time.sleep(1)
            logutil = LogUtil()
            logutil.read_log(boxsettings.LOG_FILE)
            if sender.is_online():
                self.logger.debug('sender.is_online')
                sender.send_log(logutil.log_text)
            else:
                self.logger.info('We do not send log as we are not online')
        except:
            msg = "problem occured when attempting to send the log."
            self.logger.fatal(msg)



    @abstractmethod
    def shutdown(self):
        pass


class PijuiceException(Exception):
    message = ""

    def __init__(self, msg):
        self.message = msg


class RaspiFactoryException:
    message = ""

    def __init__(self, msg):
        self.message = msg

class Raspi(RaspiFactory):
    "A real raspberry pi 3 with pijuice and sensors plate"
    name = "Raspi-3"
    pj = None # Pijuice instance

    def initSensors(self):
        self.logger.debug('waiting for I2C-1 channel...')
        count = 0
        max_count = 5
        i2cExist = False
        if os.path.exists('/dev/i2c-1'):
            i2cExist = True
        else:
            i2cExist = False
        while not os.path.exists('/dev/i2c-1'):
            count += 1
            time.sleep(5.0)
        if not i2cExist:
            self.logger.fatal("/dev/i2c-1 seems not to exist.")
            raise RaspiFactoryException("/dev/i2c-1 seems not to exist.")
        self.logger.debug('Creating sensors...')
        self.ph_probe   = Probes.factory('ph')
        self.orp_probe  = Probes.factory('orp')
        self.temp_probe = Probes.factory('temp')
        self.logger.debug('Raspi-3 initSensors DONE')

    def initPijuice(self):
        self.logger.debug('initPijuice...')
        import pijuice
        self.pj = pijuice.PiJuice(1, 0x14)
        self.logger.debug('Done.')

    def connect_pijuice(self):
        self.logger.debug('connecting pijuice to wake_up instance...')
        self.wake_up.connect_pijuice(self.pj)
        self.logger.debug('done')

    def get_charge_level(self):
        self.logger.debug('getting charge level...')
        charge = self.pj.status.GetChargeLevel()
        battery_level = charge['data']
        self.logger.debug('done')
        return battery_level

    def setup_wakeup(self):
        self.logger.debug('setup wakeup hours on pijuice...')
        self.wake_up.set_wakeup_hour_on_pijuice()
        self.logger.debug('done')
        self.logger.debug('set alarm on...')
        self.wake_up.set_wakeup_on()
        self.logger.debug('done')

    def shutdown(self):
        self.logger.debug('shutdown...')
        self.logger.debug('Shutdown of pijuice will occur in 60 seconds')
        self.wake_up.shutdown_pijuice(60)
        self.logger.debug('power off')
        self.logger.debug('done')
        subprocess.call(["sudo", "poweroff"])

    def bigshutdown(self):
        self.logger.info('Big shutdown...')
        self.wake_up.set_wakeup_off()
        self.wake_up.shutdown_pijuice(60)
        subprocess.call(["sudo", "poweroff"])

    def shutdown_later(self, minutes):
        self.logger.debug('Shutdown in %s minutes.' % minutes)
        self.wake_up.shutdown_pijuice(60*minutes+60) # 1 minute after pi shutdown, pijuice will be power off
        subprocess.call(["sudo", "shutdown" "-h" "+%s" % minutes])




# Mock object to build a mock raspi

class MockPower:
    name = "power_module"

    def __init__(self, pool_settings):
        self.pool_settings = pool_settings

    def SetPowerOff(self, seconds):
        self.logger = logging.getLogger('MockPower')
        if self.pool_settings.bigshutdown():
            self.logger.debug('BIG shutdown')
        else:
            self.logger.debug('No BIG shutdown')
        self.logger.info('MockPower: setPowerOff')


class MockPijuice:
    def __init__(self, pool_settings):
        self.logger = logging.getLogger('MockPijuice')
        self.power = MockPower(pool_settings=pool_settings)
        self.logger.debug('MockPower created')


class MockRaspi(RaspiFactory):
    "A mockup Raspberry pi"
    name = "MockupRaspi"

    def initSensors(self):
        self.logger = logging.getLogger('MockRaspi')
        self.ph_probe = Probes.factory('mock_ph')
        self.orp_probe = Probes.factory('mock_orp')
        self.temp_probe = Probes.factory('mock_temp')
        self.logger.debug('MockRaspi initSensors done')

    def get_charge_level(self):
        return 60;

    def initPijuice(self):
        from poolsettings import PoolSettings
        ps = PoolSettings()
        self.pj = MockPijuice(pool_settings=ps)
        self.logger.info('Pijuice initialised')

    def connect_pijuice(self):
        self.wake_up.connect_pijuice(self.pj)
        self.logger.info('Pijuice connected')

    def setup_wakeup(self):
        self.logger.debug('set wakeup hour of pijuice')
        self.logger.debug('set pijuice alarm ON')
        self.logger.debug('shutdown_pijuice')

    def shutdown(self):
        self.logger.info('sending log')
        self.logger.debug('shutdown pijuice')
        self.logger.debug('Shutdown of pijuice will occur in 60 seconds')
        self.send_log()
        self.logger.info('Shutdown')
        self.logger.debug('power off')


    def bigshutdown(self):
        self.logger.info('Big shutdown...')
        self.pj.power.SetPowerOff(3)

    def shutdown_later(self, minutes):
        self.logger.debug('Shutdown in %s minutes.' % minutes)
        self.wake_up.shutdown_pijuice(60*minutes+60) # 1 minute after pi shutdown, pijuice will be power off
        os.system('sudo shutdown -h +5')
        #subprocess.call(["sudo", "shutdown -h +5"])










