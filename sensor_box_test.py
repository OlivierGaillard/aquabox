import requests
import unittest
import random
from restclient import Sender
import boxsettings




class TestApi(unittest.TestCase):
    """This class simulates the work of the sensors box (Raspberry Pi).
    It can be used on the rapsberry-pi and should to test the REST service.

    It does not user Django testing framework but only normal Python.
    It is run with command: python sensor_test_pyunit.py"""

    def setUp(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD


        self.user_box2 = boxsettings.REST_USER2
        self.user_box2_passwd = boxsettings.REST_PASSWORD2


    def get_random_degree(self):
        deg_value = random.randint(3, 30)
        deg_value += random.random()
        return deg_value

    def get_random_ph(self):
        value = random.randint(3, 10)
        value += random.random()
        return value

    def get_random_redox(self):
        value = random.randint(100, 600)
        value += random.random()
        return value


    def test_degree_list_for_raspi(self):
        url = self.live_server_url + '/deg/'
        r = requests.get(url, auth=(self.user_box, self.user_box_passwd))
        self.assertEqual(r.status_code, 200)
        results = r.json()
        self.assertEqual(type(results), list)


    def test_sender_deg(self):
        sender = Sender()
        for i in range(0,8):
            if i % 2:
                sender.user_box = self.user_box2
                sender.user_box_passwd = self.user_box2_passwd
            else:
                sender.user_box = self.user_box
                sender.user_box_passwd = self.user_box_passwd

            response = sender.send_deg(self.get_random_degree())
            self.assertEqual(201, response.status_code)


    def test_delete_deg(self):
        sender = Sender()
        response = sender.send_deg(self.get_random_degree())
        self.assertEqual(201, response.status_code)
        rjson = response.json()
        id = rjson['id']
        status_code = sender.del_deg(id)
        self.assertEqual(200, status_code)

    def test_sender_ph(self):
        sender = Sender()
        response = sender.send_ph(self.get_random_ph())
        self.assertEqual(201, response.status_code)

    def test_sender_redox(self):
        sender = Sender()
        value = self.get_random_redox()
        response = sender.send_redox(value)
        self.assertEqual(201, response.status_code)

    def test_sender_deg_last(self):
        """Get last value saved"""
        sender = Sender()
        response = sender.deg_last()
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()