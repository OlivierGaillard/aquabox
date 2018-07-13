import random
from abc import ABCMeta, abstractmethod, abstractproperty
import io
import fcntl
import time
import boxsettings
import logging

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname, filemode='a', level=logging.DEBUG)

class ProbesController:

    def led_State(self):
        return 'L,?'

    def get_Led_On_Cmd(self):
        return 'L,1'

    def get_Led_Off_Cmd(self):
        return 'L,0'

    def get_ph_Cmd(self):
        return 'R'

    def translate_answer(self, answer):
        CMD_SUCCESS = 'Command succeeded'
        translations = {'?L,0' : 'Off', '?L,1' : 'On', 'Command succeeded' : 'Command succeeded' }
        answer = answer.strip()
        if answer == CMD_SUCCESS:
            return answer
        try:
            if answer.startswith(CMD_SUCCESS):
                tmp = answer.split(CMD_SUCCESS)[1].strip()
                return translations[tmp]
            return translations[answer]
        except KeyError:
            raise Exception('Unable to translate answer: "%s"' % answer)

class Probes:
    __metaclass__ = ABCMeta

    # these values are identical for all 3 probes
    NO_DATA_SEND = 255
    STILL_PROCESSING_NOT_READY = 254
    SYNTAX_ERROR = 2
    SUCCESSFUL_REQUEST = 1
    long_timeout = 1.5  # the timeout needed to query readings and calibrations
    short_timeout = .5  # timeout for regular commands

    answers = {NO_DATA_SEND : 'NO DATA SEND',
               STILL_PROCESSING_NOT_READY : 'STILL PROCESSING NOT READY',
               SYNTAX_ERROR : 'SYNTAX ERROR',
               SUCCESSFUL_REQUEST : 'SUCCESSFUL REQUEST'}

    def __init__(self):
        self.controller = ProbesController()

    def query_led_state(self):
        self.write_command(self.controller.led_State())
        time.sleep(self.long_timeout)
        response = self.read_value()
        if response:
            if not response in self.answers:
                return response
            else:
                print ("response: " + self.answers[response])
        else:
            print ("received None")
            return 'None'

    def set_led_on(self):
        self.write_command(self.controller.get_Led_On_Cmd())

    def set_led_off(self):
        self.write_command(self.controller.get_Led_Off_Cmd())

    def get_state(self):
        self.write_command('Status')



    @abstractmethod
    def read_value(self):
        pass

    @abstractmethod
    def write_command(self, cmd):
        pass

    @staticmethod
    def factory(type):
        if type == 'mock_ph':
            return MockPh()
        if type == 'ph':
            return Ph(address=boxsettings.PH_ADDRESS)
        if type == 'temp':
            return Temp(address=boxsettings.TEMP_ADDRESS)
        if type == 'orp':
            return Orp(address=boxsettings.ORP_ADDRESS)

        assert 0, "Bad probe creation type: " + type


class I2Connector:
    long_timeout = 1.5  # the timeout needed to query readings and calibrations
    short_timeout = .5  # timeout for regular commands
    default_address = 99
    current_address = default_address
    default_bus = 1
    base_bus_path = '/dev/i2c-'
    file_write = None
    file_read  = None

    def __init__(self, address):
        self.current_address = address
        self.file_write = open(self.base_bus_path + str(self.default_bus), "wb", buffering=0)
        self.file_read = open(self.base_bus_path + str(self.default_bus), "rb", buffering=0)
        self.set_i2c_address(address)

    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.current_addr = addr


class Ph(Probes):
    """
    pH_EZO based on Atlas Scientific i2c.py code
    """
    long_timeout = 1.5  # the timeout needed to query readings and calibrations
    short_timeout = .5  # timeout for regular commands
    default_address = 99
    current_address = default_address
    ready = True
    command = ''
    max_tries = 50
    tries = 0
    success = False
    probe_value = 0.0


    def __init__(self, address=default_address):

        self.controller = ProbesController()
        self.connector = I2Connector(address=address)
        self.file_write = self.connector.file_write
        self.file_read  = self.connector.file_read
        if boxsettings.FAKE_DATA:
            logging.warning('Sending fake data')

    def get_random_ph(self):
        value = random.randint(3, 10)
        value += random.random()
        return value


    def write_command(self, cmd):
        cmd += "\00"
        self.file_write.write(cmd)
        #print ('sleeping %s sec' % self.long_timeout)
        time.sleep(self.long_timeout)


    def read_value(self, num_of_bytes=31):
        res = self.file_read.read(num_of_bytes)  # read from the board
        response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
        code = ord(response[0])
        if code == self.SUCCESSFUL_REQUEST:  # if the response isn't an error
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            answer =  ''.join(char_list)
            self.success = True
            self.probe_value = answer
        elif code == self.STILL_PROCESSING_NOT_READY:
            #print ("NOT READY. ")
            pass
        else:
            print ("code inconnu: (in read_value)" + str(code))



    def get_value(self):
        nb = 0
        while self.success == False and nb < self.max_tries:
            nb += 1
            self.write_command(self.controller.get_ph_Cmd())
            self.read_value(31)
        if self.success:
            logging.info("Success: value read in %s times." % nb)
        else:
            logging.warning('Fail: unable to read value. Returning default (0.0) Tried %s times.' % nb)
        if self.probe_value < 0.0:
            self.probe_value = 0.0
        return self.probe_value

    def get_status(self):
        self.write_command('Status')
        res = self.read_value(31)
        return res

    def get_ph(self):
        if boxsettings.FAKE_DATA:
            return self.get_random_ph()
        return self.get_value()

class Temp(Ph):

    def fake_temperature(self):
        deg_value = random.randint(3, 30)
        deg_value += random.random()
        return deg_value

    def get_temp(self):
        if boxsettings.FAKE_DATA:
            return self.fake_temperature()
        return self.get_value()

class Orp(Ph):

    def get_random_redox():
        value = random.randint(100, 600)
        value += random.random()
        return value

    def get_orp(self):
        if boxsettings.FAKE_DATA:
            return self.get_random_redox()
        return self.get_value()

class MockPh(Ph):
    """
    Simulates a pH probe: receives commands and will answer.
    """

    ready = True
    command = ''
    answer = ''

    led_state = ord('L') + ord(',') + ord('0')
    ph = 7.001

    def __init__(self):
        self.controller = ProbesController()

    def _convert_to_ascii(self, str):
        tmp = ''
        for s in str:
            tmp += chr(ord(s))
        return tmp

    def set_led_on(self):
        self.led_state = ord('1')

    def set_led_off(self):
        self.led_state = ord('0')

    def get_state(self):
        return self.led_state

    def __fake_answer(self, cmd):
        """Build answer based on commmand"""
        if cmd == 'L,?':
            self.answer =  self.get_state()

    def __fake_write(self, cmd):
        if cmd == 'L,1':
            self.set_led_on()
        if cmd == 'L,0':
            self.set_led_off()


    def create_answer(self):
        ok_byte = bytes(1) # bytearray(['1'])
        end_data_marker = '\x00'
        self.answer = ok_byte + self.answer + end_data_marker

    def read_value(self, num_of_bytes=31):
        res = self.create_answer()
        response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
        code = response[0]
        if code == self.SUCCESSFUL_REQUEST:  # if the response isn't an error
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            #char_list = map(lambda x: chr(ord(x)), list(response[1:]))
            answer =  ''.join(char_list)
            self.success = True
            return  answer
        elif code == self.STILL_PROCESSING_NOT_READY:
            return code
        else:
            return code

    def write_command(self, cmd):
        self.command = cmd
        self.__fake_write(cmd)


    def get_value(self):
        self.tries += 1
        self.write_command(self.controller.get_ph_Cmd())
        res = self.read_value(31)
        if self.success:
            return res
        else:
            if self.tries < self.max_tries:
                if self.tries > 5:
                    time.sleep(2.0)
                self.get_value()
            else:
                print ("unable to get get_ph")
