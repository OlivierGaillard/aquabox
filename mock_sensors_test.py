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

    def test_create_response(self):
        ok_byte = bytes(1)
        data = [ord('L'), ord(','), ord('0')]
        end_data_marker =  ['\x00']
        answer = [ok_byte] + data + end_data_marker
        response = filter(lambda x: x != '\x00', answer)
        self.assertEqual(1, ord(response[0]))


    def btest_mock_ph_get_Led_state(self):
        mockph = Probes.factory('mock_ph')
        state = mockph.query_led_state()
        self.assertTrue(state == 'On' or state == 'Off' or state == 'Error')


    def btest_translate_answer(self):
        probectrl = ProbesController()
        answer = probectrl.translate_answer('Command succeeded ?L,0')
        self.assertEqual(answer, 'Off')


if __name__ == '__main__':
    unittest.main()
