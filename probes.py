import random
from abc import ABCMeta, abstractmethod
import fcntl
import time
import boxsettings
import logging

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
        self.logger = logging.getLogger('Probes')
        self.controller = ProbesController()
        self.logger.debug('ProbesController instance created')

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
        logger = logging.getLogger('Static Probes factory')
        if type == 'mock_ph':
            logger.debug('MockPh')
            return MockPh()
        if type == 'mock_temp':
            return MockTemp()
        if type == 'mock_orp':
            return MockOrp()
        if type == 'ph':
            logger.debug('Ph probe with address %s ' % boxsettings.PH_ADDRESS)
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
        self.logger = logging.getLogger('I2Connector')
        self.logger.debug('Init..')
        self.current_address = address
        self.file_write = open(self.base_bus_path + str(self.default_bus), "wb", buffering=0)
        self.file_read = open(self.base_bus_path + str(self.default_bus), "rb", buffering=0)
        self.set_i2c_address(address)
        self.logger.debug('done')

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
        self.logger = logging.getLogger('Ph')
        self.controller = ProbesController()
        self.connector = I2Connector(address=address)
        self.file_write = self.connector.file_write
        self.file_read  = self.connector.file_read
        if boxsettings.FAKE_DATA:
            self.logger.warning('Sending fake data')
        else:
            self.logger.info('Sending real data')
        self.logger.debug('Init done')

    def write_command(self, cmd):
        self.logger.debug('writing command %s' % cmd)
        cmd += "\00"
        self.file_write.write(cmd)
        self.logger.debug('waiting %s' % self.long_timeout)
        time.sleep(self.long_timeout)


    def read_value(self, num_of_bytes=31):
        self.logger.debug('read_value')
        res = self.file_read.read(num_of_bytes)  # read from the board
        response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
        code = ord(response[0])
        if code == self.SUCCESSFUL_REQUEST:  # if the response isn't an error
            self.logger.debug('Sucessful reading')
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            answer =  ''.join(char_list)
            self.success = True
            self.probe_value = answer
        elif code == self.STILL_PROCESSING_NOT_READY:
            self.logger.debug('NOT READY')
        else:
            self.logger.warning("code inconnu: (in read_value)" + str(code))



    def get_value(self):
        nb = 0
        while self.success == False and nb < self.max_tries:
            nb += 1
            self.write_command(self.controller.get_ph_Cmd())
            self.read_value(31)
        if self.success:
            self.logger.info("get_value: Success, value read in %s times." % nb)
        else:
            self.logger.warning('Fail: unable to read value. Returning default (0.0) Tried %s times.' % nb)
        if self.probe_value < 0.0:
            self.probe_value = 0.0
        return self.probe_value

    def get_status(self):
        self.write_command('Status')
        res = self.read_value(31)
        return res

    def get_ph(self):
        return self.get_value()


class MockPh(Probes):

    def get_random_ph(self):
        value = random.randint(3, 10)
        value += random.random()
        self.logger.debug('MockPh value: %s' % value)
        return value

    def read_value(self):
        return self.get_random_ph()

    def write_command(self, cmd):
        self.logger.debug('cmd: %s' % cmd)

    def get_ph(self):
        return self.get_random_ph()


class Temp(Ph):

    def get_temp(self):
        self.logger.debug('Getting temperature')
        return self.get_value()

class MockTemp(Probes):

    def fake_temperature(self):
        deg_value = random.randint(3, 30)
        deg_value += random.random()
        return deg_value

    def get_temp(self):
        self.logger.debug('Returning fake temperature')
        return self.fake_temperature()

    def read_value(self):
        return self.fake_temperature()

    def write_command(self, cmd):
        self.logger.debug('cmd: %s' % cmd)



class Orp(Ph):

    def get_orp(self):
        return self.get_value()

class MockOrp(Probes):

    def get_random_redox(self):
        value = random.randint(100, 600)
        value += random.random()
        return value

    def get_orp(self):
        val = self.get_random_redox()
        self.logger.debug('MockOrp value %s' % val)
        return val

    def read_value(self):
        return self.get_random_redox()

    def write_command(self, cmd):
        self.logger.debug('cmd: %s' % cmd)


