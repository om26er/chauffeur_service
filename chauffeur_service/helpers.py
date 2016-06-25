import os
import configparser

CONFIG_SECTION_DEFAULT = 'defaults'
CONFIG_SECTION_EMAIL_CREDENTIALS = 'email_credentials'
CONFIG_SECTION_DATABASE_CREDENTIALS = 'database_credentials'


class ConfigHelpers:

    def __init__(self, config_file):
        self.config_file = config_file
        if os.path.isfile(self.config_file):
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file)
        else:
            raise RuntimeError('Config file does not exist.')

    def read_config_parameter(self, config_section, config_key):
        try:
            return self.config.get(config_section, config_key)
        except configparser.NoOptionError or configparser.NoSectionError:
            return None

    def get_email_credential_by_key(self, key):
        return self.read_config_parameter(
            CONFIG_SECTION_EMAIL_CREDENTIALS,
            key
        )

    def get_database_credential_by_key(self, key):
        return self.read_config_parameter(
            CONFIG_SECTION_DATABASE_CREDENTIALS,
            key
        )

    def get_debug_setting(self):
        value = self.read_config_parameter(CONFIG_SECTION_DEFAULT, 'debug')
        return value == 'True'
