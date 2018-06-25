#!/usr/bin/python

""" Get the temperature and send it to the REST service"""

import serial
import logging
from restclient import Sender
import boxsettings
from thermometer import Thermometer
import random


logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.DEBUG)


class GetSendTemp:

    def __init__(self):
        self.temperature = 0
        if not boxsettings.FAKE_DATA:
            logging.debug("Not FAKE data")
            self.thermometer = Thermometer()
        else:
            logging.debug("Not using sensors: fake data.")

    def fake_temperature(self):
        deg_value = random.randint(3, 30)
        deg_value += random.random()
        return deg_value

    def measure_temperature(self):
        if boxsettings.FAKE_DATA:
            self.temperature = self.fake_temperature()
            logging.debug("Fake temperature: %s", self.temperature)
        else:
            try:
                self.temperature = self.thermometer.read_temp()
                logging.info("Temperature was read: %s", str(self.temperature))
            except:
                logging.warning("Error when reading temperature.")


    def send_temperature(self):
        logging.debug('GetSendTemp: send_temperature')
        sender = Sender()
        sender.send_deg(self.temperature)



def main():
    temperature_controler = GetSendTemp()
    temperature_controler.measure_temperature()
    temperature_controler.send_temperature()
    print "Temperature:", str(temperature_controler.temperature), "sent to service."

if __name__ == '__main__':
    main()
