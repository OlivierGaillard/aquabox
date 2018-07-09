#!/usr/bin/python
import serial
import logging
from restclient import Sender
import boxsettings
import sleep
import random
from probes import Probes

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.DEBUG)



class GetSendPh:
    """
    This class use one factory to use the pH sensor (real or mock).
    """

    def __init__(self):
        self.ph = 0
        self.usbport = boxsettings.USB_PORT
        if boxsettings.FAKE_DATA:
            self.ser = None
        else:
            self.ser = serial.Serial(self.usbport, 38400, timeout=1)

    def set_random_ph(self):
        value = random.randint(3, 10)
        value += random.random()
        self.ph = value


    def readAnswer(self):
        line = ""
        count = 0
        while (True):
            count += 1
            data = self.ser.read()
            if (data == "\r" or data == ""):
                break
            else:
                line = line + data
        logging.debug("Chars read: %s", count)
        return line



    def is_pH_answer(self, pH):
        """ Check if s is in the form 3.123
        """
        answer = False
        try:
            float(pH)
            answer = True
            logging.debug('received good ph_answer: %s', pH)
        except:
            logging.debug('bad ph answer: %s', pH)
        return answer



    def measure_ph(self, trial_count, max_trial=5):
        logging.debug('In measure_ph: trial_count: %s, max_trial: %s', trial_count, max_trial)
        trial_count += 1
        if (trial_count > max_trial):
            logging.warning("Maximum trials %s was reached. Unable to get pH", max_trial)
            return 0
        logging.debug("Querying the ph...")
        self.ser.write("R\r")
        ph = self.readAnswer()
        logging.debug("getPh: Answer: %s", ph)

        if ph == "*OK":
            logging.debug("pH ready to be read")
            return self.measure_ph(trial_count, max_trial)
        elif self.is_pH_answer(ph) == True:
            logging.debug("pH was received")
            logging.debug("Trials count: %s", trial_count)
            self.ser.close()
            self.ph = float(ph)
        else:
            logging.debug("Not ready to read pH. Retrying...")
            return self.measure_ph(trial_count, max_trial)


    def send_ph(self):
        logging.debug('GetSendPh')
        sender = Sender()
        sender.send_ph(self.ph)




def main():
    logging.info('Start pH measure')
    p = GetSendPh()
    if not boxsettings.FAKE_DATA:
        logging.info('True data. calling measure_ph')
        p.measure_ph(1, 5)
    else:
        logging.warning('FAKE-DATA')
        p.set_random_ph()
    logging.info('pH: %s', p.ph)
    #p.send_ph()
    #logging.debug('pH sent to service')
    # if not boxsettings.FAKE_DATA:
    #     logging.info("Setting sensor in sleeping mode.")
    #     sleep.startSleep()
    print 'pH:', p.ph
    logging.info("End of pH measure")

if __name__ == '__main__':
    main()
