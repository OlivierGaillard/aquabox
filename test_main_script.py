import unittest
import boxsettings
from box import RaspiFactory
from read_and_send import PoolMaster
import logging
from poolsettings import PoolSettings
from log import LogUtil
from restclient import Sender



class TestMainScript(unittest.TestCase):
    """ """

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD

    def btest_get_fake_measures(self):
        raspi = RaspiFactory.getRaspi('Mock')
        self.assertIsNotNone(raspi.get_temp_from_pi())
        self.assertIsNotNone(raspi.get_charge_level())
        self.assertIsNotNone(raspi.get_ph_from_pi())
        self.assertIsNotNone(raspi.get_orp_from_pi())

    def btest_get_real_measures(self):
        print "In test_get_real_measures"
        raspi = RaspiFactory.getRaspi('Raspi')
        self.assertIsNotNone(raspi.get_temp_from_pi())
        self.assertIsNotNone(raspi.get_charge_level())
        self.assertIsNotNone(raspi.get_ph_from_pi())
        self.assertIsNotNone(raspi.get_orp_from_pi())


    def test_poolmaster(self): # if boxsettings has FAKE_DATA = True or not
        poolmaster = PoolMaster()
        poolmaster.read_measures()
        self.assertTrue(poolmaster.readings_done)
        poolmaster.send_measures()
        self.assertTrue(poolmaster.sendings_done)

    def btest_send_charge_level(self):
        raspi = RaspiFactory.getRaspi('Mock')
        sender = Sender()
        response = sender.send_battery_level(raspi.get_charge_level())
        self.assertEqual(201, response.status_code)

    def btest_pool_settings(self):
        pool_settings = PoolSettings()
        log_util = LogUtil()
        log_level = log_util.get_log_level(pool_settings.log_level())
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        logger.debug('Log level: %s' % log_level)



if __name__ == '__main__':
    logname = boxsettings.LOG_FILE
    logging.basicConfig(format='%(levelname)s\t: %(name)s\t: %(asctime)s : %(message)s', filename=logname, filemode='w',
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    unittest.main()
