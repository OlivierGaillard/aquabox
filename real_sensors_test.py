#import requests
import unittest
import random
#from restclient import Sender
import boxsettings
from probes import Probes, ProbesController
#from get_and_send_ph import GetSendPh
import time


class TestSensors(unittest.TestCase):
    """This class simulates the work of the sensors box (Raspberry Pi).
    It can be used on the rapsberry-pi and should to test the REST service.

    It does not user Django testing framework but only normal Python.
    It is run with command: python sensor_test_pyunit.py"""

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD

    def test_get_pH(self):
        print( "pH test: value")
        ph = Probes.factory('ph')  # real pH probe
        ph_value = ph.get_ph()
        print('pH is : %s' % ph_value)
        self.assertTrue(float(ph_value) > 0.0)

    def test_orp(self):
        print ('ORP test')
        orp = Probes.factory('orp')
        print(orp.get_orp())

    def btest_translate_answer(self):
        probectrl = ProbesController()
        answer = probectrl.translate_answer('Command succeeded ?L,0')
        self.assertEqual(answer, 'Off')

    def test_temperature(self):
        t = Probes.factory('temp')
        print ('querying temperature')
        temp = t.get_temp()

if __name__ == '__main__':
    unittest.main()
