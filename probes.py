import random
from abc import ABCMeta, abstractmethod, abstractproperty
import io
import fcntl
import time

class ProbesController:




    def led_State(self):
        return 'L,?'

    def get_Led_On_Cmd(self):
        return 'L,1'

    def get_Led_Off_Cmd(self):
        return 'L,0'

    def translate_answer(self, answer):
        CMD_SUCCESS = 'Command succeeded'
        translations = {'Error 254' : 'Error', '?L,0' : 'Off', '?L,1' : 'On', 'Command succeeded' : 'Command succeeded' }
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
        return self.controller.translate_answer(response)

    def set_led_on(self):
        self.write_command(self.controller.get_Led_On_Cmd())

    def set_led_off(self):
        self.write_command(self.controller.get_led_Off_Comd())

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
            return Ph()

        assert 0, "Bad probe creation type: " + type




class MockPh(Probes):
    """
    Simulates a pH probe: receives commands and will answer.
    """

    default_address = 99
    current_address = default_address
    default_bus = 1
    base_bus_path = 'i2c-'
    ready = True
    command = ''


    def __init__(self, address=default_address, bus=default_bus):

        self.file_write = open(self.base_bus_path + str(bus), "wb", buffering=0)
        self.file_read  = open(self.base_bus_path + str(bus), "rb", buffering=0)
        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)
        self.controller = ProbesController()


    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        # fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        # fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.current_addr = addr

    # def write(self, cmd):
    #     # appends the null character and sends the string over I2C
    #     cmd += "\00"
    #     self.file_write.write(cmd)

    def set_not_ready(self):
        self.ready = False

    def create_answer(self, data):
        ok_byte = bytearray(['1'])
        end_data_marker = '\x00'
        answer = ok_byte + data + end_data_marker
        return answer

    def read_value(self):
        if self.command == 'L,?':
            res = self.create_answer('L,0')
            response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
            print "response[0]: " + str(ord(response[0]))
            if ord(response[0]) == self.SUCCESSFUL_REQUEST:  # if the response isn't an error
                # change MSB to 0 for all received characters except the first and get a list of characters
                # char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
                print self.answers[self.SUCCESSFUL_REQUEST]
                char_list = map(lambda x: chr(ord(x)), list(response[1:]))
                answer = ''.join(char_list)
                if len(answer) == 0:
                    print "answer empty"
                    print "retrying. wait 3 seconds"
                    time.sleep(3.0)
                    self.read_value(num_of_bytes=31)
                else:
                    print "answer not empty"
                return answer
                # NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
            else:
                print "error arises"
                return self.answers[ord(response[0])]

    def write_command(self, cmd):
        self.command = cmd



class Ph(Probes):
    """
    pH_EZO based on Atlas Scientific i2c.py code
    """
    long_timeout = 1.5  # the timeout needed to query readings and calibrations
    short_timeout = .5  # timeout for regular commands
    default_address = 99
    current_address = default_address
    default_bus = 1
    base_bus_path = '/dev/i2c-'
    ready = True
    command = ''


    def __init__(self, address=default_address, bus=default_bus):

        self.file_write = open(self.base_bus_path + str(bus), "wb", buffering=0)
        self.file_read  = open(self.base_bus_path + str(bus), "rb", buffering=0)
        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)
        self.controller = ProbesController()


    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.current_addr = addr


    def read_value(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C, then parses and displays the result
        res = self.file_read.read(num_of_bytes)  # read from the board
        print "res: " + res
        response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
        print "response[0]: " + str(ord(response[0]))
        if ord(response[0]) == self.SUCCESSFUL_REQUEST:  # if the response isn't an error
            # change MSB to 0 for all received characters except the first and get a list of characters
            #char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            print self.answers[self.SUCCESSFUL_REQUEST]
            char_list = map(lambda x: chr(ord(x)), list(response[1:]))
            answer =  ''.join(char_list)
            if len(answer) == 0:
                print "answer empty"
                print "retrying. wait 3 seconds"
                time.sleep(3.0)
                self.read_value(num_of_bytes=31)
            else:
                print "answer not empty"
            return answer
            # NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
        else:
            print "error arises"
            return self.answers[ord(response[0])]



    def write_command(self, cmd):
        cmd += "\00"
        self.file_write.write(cmd)
