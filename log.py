import logging

class LogUtil:
    """Read the log file 'rest.log' and make its content available for Sender"""

    log_text = ""
    log_level = {'DEBUG' : logging.DEBUG,
                 'INFO' : logging.INFO,
                 'ERROR' : logging.ERROR,
                 'CRITICAL' : logging.CRITICAL,
                 'FATAL' : logging.FATAL}

    def read_log(self, log_file):
        log_file = log_file
        f = open(log_file, 'r')
        self.log_text = f.read()

    def get_log_level(self, log_level_config_str):
        "Given the log_level string it return the logging level instance"
        try:
            return self.log_level[log_level_config_str]
        except KeyError:
            raise "not a valid log level received from pool settings: %s" % log_level_config_str

