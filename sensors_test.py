import requests
import unittest
import random
from restclient import Sender
import boxsettings
from get_and_send_ph import GetSendPh




class TestSensors(unittest.TestCase):
    """This class simulates the work of the sensors box (Raspberry Pi).
    It can be used on the rapsberry-pi and should to test the REST service.

    It does not user Django testing framework but only normal Python.
    It is run with command: python sensor_test_pyunit.py"""

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD


    def test_get_ph(self):
        ph = GetSendPh()
        ph.measure_ph(trial_count=1, max_trial=5)
        print(ph.ph)
        self.assertTrue(ph.ph > 0.0)



if __name__ == '__main__':
    unittest.main()
