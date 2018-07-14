import requests
import logging
import unittest
import random
from datetime import datetime
from restclient import Sender
import boxsettings
from poolsettings import PoolSettings, HoursUtils
#from shutdown import WakeUp
from urllib3.exceptions import NewConnectionError


class TestApi(unittest.TestCase):
    """
    Test class for Wakeup: starting hour setup
    """

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD


    def get_random_hour(self):
        hour = random.randint(1, 24)
        return hour


    def test_hours_of_readings(self):
        settings = PoolSettings()
        self.assertIsNotNone(settings.hours_of_readings())

    def test_get_starting_hour(self):
        settings = PoolSettings()
        self.assertEqual('8,13,19', settings.hours_of_readings())

    def test_get_hours_list(self):
        hours_enum_bern = '8,13,19'
        hoursutil = HoursUtils(hours_enum=hours_enum_bern, current_hour=8)
        self.assertEqual([6, 11, 17], hoursutil.hours)

    def test_get_next_reading_hour_given_current_hour_in_utc(self):
        hours_enum = '8,13,19' # Zurich time
        current_hour_utc = 7
        hoursutil = HoursUtils(hours_enum, current_hour_utc)
        self.assertEqual(11, hoursutil.next_reading_hour())

    def test_get_next_reading(self):
        """next reading in time zone bern"""
        hours_enum = '8,13,19'  # Zurich time
        current_hour_utc = 7
        hoursutil = HoursUtils(hours_enum, current_hour_utc)
        self.assertEqual(11, hoursutil.next_reading_hour())
        self.assertEqual(13, hoursutil.next_reading_hour_local())


if __name__ == '__main__':
    #logname = '/home/pi/phweb/box/rest.log'
    logname = 'rest.log'
    logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='a', level=logging.DEBUG)

    unittest.main()
