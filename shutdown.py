from __future__ import print_function
import time
import pijuice
import subprocess
import datetime
import os
import sys
import logging
from restclient import Sender

DELTA_MIN = 10
def main():
    # Rely on RTC to keep the time
    subprocess.call(["sudo", "hwclock", "--hctosys"])
    # This script is started at reboot by cron.
    # Since the start is very early in the boot sequence we wait for the i2c-1 device
    while not os.path.exists('/dev/i2c-1'):
        time.sleep(5.0)

    try:
        pj = pijuice.PiJuice(1, 0x14)
    except:
        logging.fatal("Cannot create pijuice object")
        print("Cannot create pijuice object")
        sys.exit()

    a = {}
    a['year'] = 'EVERY_YEAR'
    a['month'] = 'EVERY_MONTH'
    a['day'] = 'EVERY_DAY'
    a['hour'] = 'EVERY_HOUR'
    t = datetime.datetime.utcnow()
    a['minute'] = (t.minute + DELTA_MIN) % 60
    #a['minute'] = 0
    a['second'] = 0
    status = pj.rtcAlarm.SetAlarm(a)
    if status['error'] != 'NO_ERROR':
        print('Cannot set alarm\n')
        logging.warning('Cannot set alarm')
        sys.exit()
    else:
        logging.info('Alarm set for %s' % str(pj.rtcAlarm.GetAlarm()))
        print('Alarm set for ' + str(pj.rtcAlarm.GetAlarm()))

    # Enable wakeup, otherwise power to the RPi will not be
    # applied when the RTC alarm goes off
    pj.rtcAlarm.SetWakeupEnabled(True)
    time.sleep(0.4)

    # PiJuice shuts down power to Rpi after 20 sec from now
    # This leaves sufficient time to execute the shutdown sequence
    sender = Sender()
    enable_shutdown = sender.get_shutdown_settings()
    if enable_shutdown:
        logging.info('We will MAKE a shutdown')
        print('We will MAKE a shutdown')
        pj.power.SetPowerOff(20)
        subprocess.call(["sudo", "poweroff"])
    else:
        print('We do NOT make a shutdown')
        logging.info('We do NOT make a shutdown')


if __name__ == '__main__':
    main()

