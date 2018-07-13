import json

class PoolSettings:
    """Encapsulates pool settings like:
    - shutdown enable
    - next wakeup
    - do update
    """

    settings = {}

    def __init__(self, settings_json):
        self.settings = settings_json

    def enable_shutdown(self):
        enable_shutdown = self.settings['enable_shutdown']
        return enable_shutdown

    def do_update(self):
        return self.settings['do_update']

    def time_beetween_readings(self):
        return self.settings['time_beetween_readings']