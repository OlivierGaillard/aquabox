import requests
import unittest
import random
from restclient import Sender
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

    def test_get_real_pH_Led_state(self):
        ph = Probes.factory('ph') # real pH probe
        for i in range(0,3):
            state = ph.query_led_state()
            print "pH Led state: '%s'" % state
            print "ON"
            print(ph.set_led_on())
            time.sleep(3)
            print "OFF"
            print(ph.set_led_off())
            print "get pH value"
            print(ph.get_ph())

    def btest_translate_answer(self):
        probectrl = ProbesController()
        answer = probectrl.translate_answer('Command succeeded ?L,0')
        self.assertEqual(answer, 'Off')


if __name__ == '__main__':
    unittest.main()
