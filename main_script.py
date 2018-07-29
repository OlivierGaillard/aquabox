from __future__ import print_function
import pijuice
import subprocess
import logging
from restclient import Sender
from shutdown import WakeUp
import time
from poolsettings import PoolSettings
from read_and_send import PoolMaster
import boxsettings
from log import LogUtil


def do_update(pool_settings):
    # Checking if an update is required
    if pool_settings.do_update() and pool_settings.is_online():
        logging.info('We will make a git pull')
        subprocess.call(["git", "pull"])
        logging.info('Update done')
    else:
        logging.info('We do NOT make a git pull')

def take_measures(pool_settings):
    if pool_settings.enable_reading() and pool_settings.is_online():
        logging.info('We will make reading')
        poolMaster = PoolMaster()
        poolMaster.read_measures()
        poolMaster.send_measures()
        logging.info('End of JOB')
    else:
        logging.info('We do not take readings.')

def send_battery_charge_level(pool_settings):
    try:
        pj = pijuice.PiJuice(1, 0x14)
        sender = Sender()
        charge = pj.status.GetChargeLevel()
        battery_level = charge['data']
        logging.info('Battery charge in percent: %s' % battery_level)
        if pool_settings.is_online():
            logging.info('Sending info to REST')
            response = sender.send_battery_level(battery_level)
            logging.info('Answer: %s' % response.status_code)
        else:
            logging.info(('Off-line. Battery level not sent'))
    except:
        logging.fatal("Cannot create pijuice object")



def main(pool_settings):
    time.sleep(30)  # to wait for network goes up
    try:

        # If update is required
        do_update(pool_settings)

        # Taking readings eventually
        take_measures(pool_settings)

        send_battery_charge_level(pool_settings)


        # Schedule next wakeup and doing shutdown
        wake_up = WakeUp(pool_settings)
        wake_up.prepare_wakeup()
        wake_up.do_shutdown()
    except:
        time.sleep(10)
        logutil = LogUtil()
        logutil.read_log(boxsettings.LOG_FILE)
        try:
            sender = Sender()
            sender.send_log(logutil.log_text)
        except:
            msg = "problem occured when attempting to send the log."
            logging.fatal(msg)


if __name__ == '__main__':
    logname = boxsettings.LOG_FILE
    pool_settings = PoolSettings()
    # PoolSettings is able to handle off-line case
    # and will decide if update and readings will be made.
    log_util = LogUtil()
    log_level = log_util.get_log_level(pool_settings.log_level())
    logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='w',
                        level=log_level)
    main(pool_settings)




