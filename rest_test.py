import requests
import logging
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


    def btest_degree_list_for_raspi(self):
        url = self.live_server_url + '/deg/'
        r = requests.get(url, auth=(self.user_box, self.user_box_passwd))
        self.assertEqual(r.status_code, 200)
        results = r.json()
        self.assertEqual(type(results), list)


    def btest_sender_deg(self):
        logging.info('testing deg send...')
        sender = Sender()
        for i in range(0,2):
            if i % 2:
                pass
            else:
                sender.user_box = self.user_box
                sender.user_box_passwd = self.user_box_passwd

            response = sender.send_deg(self.get_random_degree())
            self.assertEqual(201, response.status_code)
        logging.info('DONE')


    def btest_delete_deg(self):
        sender = Sender()
        response = sender.send_deg(self.get_random_degree())
        self.assertEqual(201, response.status_code)
        rjson = response.json()
        id = rjson['id']
        status_code = sender.del_deg(id)
        self.assertEqual(200, status_code)

    def btest_sender_ph(self):
        logging.info('pH sending test')
        sender = Sender()
        response = sender.send_ph(self.get_random_ph())
        logging.info('pH sent. Response: %s' % response.status_code)
        self.assertEqual(201, response.status_code)

    def btest_sender_redox(self):
        sender = Sender()
        value = self.get_random_redox()
        response = sender.send_redox(value)
        self.assertEqual(201, response.status_code)

    def btest_sender_deg_last(self):
        """Get last value saved"""
        sender = Sender()
        response = sender.deg_last()
        self.assertEqual(response.status_code, 200)


    def btest_get_shutdown_instruction(self):
        sender = Sender()
        enable_shutdown = sender.get_shutdown_settings()
        if enable_shutdown:
            print('Shutdown enabled.')
        else:
            print('Shutdown disabled')
        self.assertIsNotNone(enable_shutdown, "REST returned None in place of true / false")


    def btest_get_update_instruction(self):
        sender = Sender()
        do_update = sender.get_update_settings()
        if do_update:
            print('Update will be made.')
        else:
            print('No update')
        self.assertIsNotNone(do_update, "REST returned None in place of true / false")

    def test_sender_batterycharge(self):
        sender = Sender()
        value = 10
        response = sender.send_battery_level(value)
        print response.json()
        self.assertEqual(201, response.status_code)



if __name__ == '__main__':
    #logname = '/home/pi/phweb/box/rest.log'
    logname = 'rest.log'
    logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='a', level=logging.DEBUG)

    unittest.main()
