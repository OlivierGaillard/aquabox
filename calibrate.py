#!/usr/bin/python

import serial
import logging
import sys




logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename='ph.log', filemode='a', level=logging.DEBUG)

usbport = '/dev/ttyAMA0'
ser = serial.Serial(usbport, 38400, timeout=1)

MAX_TRIAL = 10 # Maximum amount of tries to get answer
trial_count = 0

print "usage: calibrate 'mid or low or high' ph_value"

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

calib_msg = {'?CAL,0' : 'Not calibrate',
             '?CAL,1' : 'Single point calibration',
             '?CAL,2' : 'Two point calibration',
             '?CAL,3' : 'Three point calibration'}



def getCalibration():
    global trial_count
    trial_count += 1
    if (trial_count > MAX_TRIAL):
        logging.fatal("Maximum trials %s was reached when trying to get calibration's state.", MAX_TRIAL)
        sys.exit(0)
    logging.debug("Querying the calibration state...")
    ser.write("Cal,?\r")
    t = readAnswer()
    if t == "*OK":
        logging.debug("ready to be read")
        return getCalibration()
    elif t.startswith('?CAL'):
        logging.debug("Calibration state was received: %s", t)
        logging.debug("Trials count: %s", trial_count)
        return t
    else:
        logging.debug("Not ready. Retrying...")
        return getCalibration()
    logging.info("State of calibration is: %s", t)
    if t in calib_msg.keys():
        logging.info("Human readable: %s", calib_msg[t])
        return calib_msg[t]

	return s



def calibrate(calibration_point, ph_val):
    """ The medium calibration point is mandatory.
	If is achieved the other points will be cleared
	and should be calibrated again.
	The behaviour of the circuit is such that it is
	not possible to directly set the pH. It requires
	first a query of the calibration's state.
	"""

    logging.debug("Calibrating the %s point.", calibration_point)
    logging.debug("with pH value: %s", ph_val)
    if (calibration_point == 'mid'):
	    logging.warning("Medium calibration point will be made.")
	    logging.warning("Low and high calibration points will be cleared.")

    logging.info("Getting first calibration state: %s", getCalibration())

    cmd = "Cal,%s,%s\r" % (calibration_point, ph_val)
    logging.debug("Command: %s", cmd)
    ser.write(cmd)
    t = readAnswer()
    logging.debug("Answer: %s", t)
    
    if t == "*OK":
        logging.debug("Calibration was made.")
    else:
	    logging.warning("Not awaited answer.")
    return t



def clear():
    logging.info("Clearing calibrations made")
    logging.info("Getting calibration state first.")
    cal_state = getCalibration()
    logging.info("Calibration state: %s", cal_state)
    logging.info("Will clear...")
    ser.write("Cal,clear\r")
    s = readAnswer()
    print "Answer:", s
    logging.info("Answer: %s", s)


logging.debug("calibrate: Argv length: %s", len(sys.argv))
if len(sys.argv) < 2:
    print "Getting calibration state..."
    state = getCalibration()
    print 'State is: ', calib_msg[state]
    print "Don't forget to set the temperature before calibrating."
elif sys.argv[1] == 'clear':
    print "Will clear calibration"
    clear()
elif len(sys.argv) == 3:
    cal_point = sys.argv[1]
    ph_val = sys.argv[2]
    state = getCalibration()
    print 'State is: ', calib_msg[state]
    print "Calibrating with *%s* point and pH value of %s" % (cal_point, ph_val)
    print calibrate(cal_point, ph_val)




logging.debug("Closing port...")
ser.close()
if not(ser.isOpen()):
	logging.debug("Closed.")
else:
    logging.warning("Cannot close the connection to ph-circuit.")
logging.debug("End of job")
