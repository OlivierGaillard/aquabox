import os
import glob
import time


class Thermometer:
    def __init__(self):
        self.device_file = self.modprobe()


    def modprobe(self):
        os.system('sudo modprobe w1-gpio')
        os.system('sudo modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        print 'device_folder:', device_folder

        device_file = device_folder + '/w1_slave'
        print 'device_file:', device_file
        return device_file

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
	

if __name__ == "__main__":
	tmesurer = Thermometer()
    	t = tmesurer.read_temp()
	print t
