#!/usr/bin/python

import serial
import logging
import sys

usbport = '/dev/ttyAMA0'
ser = serial.Serial(usbport, 38400, timeout=1)

logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename='ph.log', filemode='a', level=logging.DEBUG)

def readAnswer():
    line = ""
    count = 0
    while (True):
        count += 1
        data = ser.read()
        if (data == "\r" or data == ""):
            break
        else:
            line = line + data
    logging.debug("Chars read: %s", count)
    return line


def startSleep():
    s = ""
    logging.debug('startSleep')
    ser.write("SLEEP\r")
    s = readAnswer()
    
    if s == "*ER":
        logging.info("Not ready. Retrying...")
        return startSleep()
    elif s == '*OK':
	    logging.info(s)
    elif s == '*WA':
        logging.info("Already in sleeping mode: %s", s)
    else:
        logging.warning("Unexpected answer. Waited *OK but received %s", s)
        sys.exit(1)
    return s


if __name__ == '__main__':
    
    print "Entering sleeping mode..."
    s = startSleep()
    print s



    logging.debug("Closing port...")
    ser.close()
    if not(ser.isOpen()):
        logging.debug("Closed.")
    logging.debug("End of job")
