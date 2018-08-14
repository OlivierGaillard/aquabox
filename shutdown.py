from __future__ import print_function
import time
import logging
from poolsettings import PoolSettings, HoursUtils
from log import LogUtil
import boxsettings
from restclient import Sender

class PijuiceAlarmException(Exception):
    message = ""

    def __init__(self, msg):
        self.message = msg

class WakeUp:

    pj = None

    def __init__(self, poolSettings):
        self.logger = logging.getLogger('WakeUp')
        self.pool_settings = poolSettings
        self.hoursUtil = HoursUtils(self.pool_settings.hours_of_readings())
        self.alarm_time = {'year'  : 'EVERY_YEAR',
                           'month' : 'EVERY_MONTH',
                           'day'   : 'EVERY_DAY',
                           'hour'  : 0,
                           'minute' : 0,
                           'second' : 0}
        self.prepare_wakeup_hour()



    def prepare_wakeup_hour(self):
        """Hours data for wakeup."""
        self.logger.info('Retrieving hours of readings')
        self.next_hour = self.hoursUtil.next_reading_hour()
        self.logger.info('Next reading hour in local time: %s' % self.hoursUtil.next_reading_hour_local())
        self.alarm_time['hour'] = self.hoursUtil.next_reading_hour()

    def connect_pijuice(self, pj):
        self.pj = pj

    def set_wakeup_hour_on_pijuice(self):
        self.logger.debug('setting wakeup hours on pijuice...')
        try:
            status = self.pj.rtcAlarm.SetAlarm(self.alarm_time)
            if status['error'] != 'NO_ERROR':
                self.logger.warning('Cannot set alarm')
                raise PijuiceAlarmException(msg='prepare_wakeup: I cannot set alarm')
            else:
                self.logger.info('Alarm set for %s UTC' % str(self.pj.rtcAlarm.GetAlarm()))
        except Exception, e:
            self.logger.warning('set_wakeup_hour: failed to set wakeup hour', exc_info=True)


    def set_wakeup_on(self):
        """Enable alarm"""
        # Enable wakeup, otherwise power to the RPi will not be
        # applied when the RTC alarm goes off
        self.logger.debug('setting alarm ON...')
        try:
            self.pj.rtcAlarm.SetWakeupEnabled(True)
            time.sleep(2.0)
            self.logger.debug('done')
        except Exception, e:
            self.logger.warning('Wakeup: failed to enable wakeup.', exc_info = True)

    def send_logfile(self):
        self.logger.info('Sending log file')
        try:
            sender = Sender()
            logger.info('Bye bye.')
            time.sleep(10)
            logutil = LogUtil()
            logutil.read_log(boxsettings.LOG_FILE)
            sender.send_log(logutil.log_text)
            self.logger.debug('done')
        except Exception, e:
            msg = "problem occured when attempting to send the log."
            self.logger.fatal(msg, exc_info=True)

    def shutdown_pijuice(self, seconds):
        # PiJuice shuts down power to Rpi after 20 sec from now
        # This leaves sufficient time to execute the shutdown sequence
        # checking if an update is required
        # checking if a shutdown should be made
        self.logger.debug('shutdown of pijuice...')
        if self.pool_settings.enable_shutdown():
            self.logger.info('We will MAKE a shutdown in %s seconds.' % seconds)
            self.pj.power.SetPowerOff(seconds) # 20
        else:
            self.logger.info('Settings do not plan a shutdown')


if __name__ == '__main__':
    pool_settings = PoolSettings()
    wake_up = WakeUp(poolSettings=pool_settings)
    wake_up.prepare_wakeup_hour()
    wake_up.set_wakeup_on()
    wake_up.shutdown_pijuice()

