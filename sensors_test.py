import requests
import unittest
import random
from restclient import Sender
import boxsettings
from probes import Probes, ProbesController
#from get_and_send_ph import GetSendPh





class TestSensors(unittest.TestCase):
    """This class simulates the work of the sensors box (Raspberry Pi).
    It can be used on the rapsberry-pi and should to test the REST service.

    It does not user Django testing framework but only normal Python.
    It is run with command: python sensor_test_pyunit.py"""

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD

    def test_mock_ph_get_Led_state(self):
        mockph = Probes.factory('mock_ph')
        state = mockph.query_led_state()
        print 'State: ' + state
        self.assertTrue(state == 'On' or state == 'Off' or state == 'Error')

    def test_get_real_pH_Led_state(self):
        ph = Probes.factory('ph') # real pH probe
        state = ph.query_led_state()
        print "state: '%s'" % state
        self.assertTrue(state == 'On' or state == 'Off' or state == 'Error')

    def test_translate_answer(self):
        probectrl = ProbesController()
        answer = probectrl.translate_answer('Command succeeded ?L,0')
        self.assertEqual(answer, 'Off')

    # def btest_get_ph(self):
    #     ph = GetSendPh()
    #     ph.measure_ph(trial_count=1, max_trial=5)
    #     print(ph.ph)
    #     self.assertTrue(ph.ph > 0.0)
    #


if __name__ == '__main__':
    unittest.main()
