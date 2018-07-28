from __future__ import print_function
import time
import pijuice
import subprocess
import datetime
import sys
import logging
from poolsettings import PoolSettings, HoursUtils



class WakeUp:

    pj = None

    def __init__(self, poolSettings):
        self.pool_settings = poolSettings

        if not self.is_pijuice_available():
            logging.fatal('As pijuice fails we eventually shutdown now.')
            if self.pool_settings.enable_shutdown():
                logging.info('Shutdown')
                self.shut_down()
            else:
                logging.info('No shutdown now.')

        t = datetime.datetime.utcnow()
        self.hoursUtil = HoursUtils(self.pool_settings.hours_of_readings(), t.hour)




    def is_pijuice_available(self):
        try:
            self.pj = pijuice.PiJuice(1, 0x14)
            return True
        except:
            logging.fatal("Cannot create pijuice object")
            print("Cannot create pijuice object")
            return False

    def shut_down(self):
        subprocess.call(["sudo", "poweroff"])


    def prepare_wakeup(self):
            # Rely on RTC to keep the time
        #subprocess.call(["sudo", "hwclock", "--hctosys"])
        a = {}
        a['year'] = 'EVERY_YEAR'
        a['month'] = 'EVERY_MONTH'
        a['day'] = 'EVERY_DAY'
        # a['hour'] = 'EVERY_HOUR'


        logging.info('Retrieving hours of readings')

        self.next_hour = self.hoursUtil.next_reading_hour()
        logging.info('Next reading hour in local time: %s' % self.hoursUtil.next_reading_hour_local())


        a['hour'] = self.hoursUtil.next_reading_hour()
        a['minute'] = 0
        a['second'] = 0
        status = self.pj.rtcAlarm.SetAlarm(a)
        if status['error'] != 'NO_ERROR':
            print('Cannot set alarm\n')
            logging.warning('Cannot set alarm')
            sys.exit()
        else:
            logging.info('Alarm set for %s UTC' % str(self.pj.rtcAlarm.GetAlarm()))
            print('Alarm set for %s UTC' % str(self.pj.rtcAlarm.GetAlarm()))

        # Enable wakeup, otherwise power to the RPi will not be
        # applied when the RTC alarm goes off
        self.pj.rtcAlarm.SetWakeupEnabled(True)
        time.sleep(1.0)

    def do_shutdown(self):

        # PiJuice shuts down power to Rpi after 20 sec from now
        # This leaves sufficient time to execute the shutdown sequence
        # checking if an update is required
        # checking if a shutdown should be made
        if self.pool_settings.enable_shutdown():
            logging.info('We will MAKE a shutdown')
            print('We will MAKE a shutdown')
            self.pj.power.SetPowerOff(20)
            self.shut_down()
        else:
            print('We do NOT make a shutdown')
            logging.info('We do NOT make a shutdown')


if __name__ == '__main__':
    pool_settings = PoolSettings()
    wake_up = WakeUp(poolSettings=pool_settings)
    wake_up.prepare_wakeup()
    wake_up.do_shutdown()

