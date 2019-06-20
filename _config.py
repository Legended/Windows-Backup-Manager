from configparser import ConfigParser
from os import getenv, mkdir, path


class Config:
    """Creates a folder and config file in 'C:/Users/<User_Name>/Documents'. This class is native only to Windows.
    Format for 'config.ini':

    [Last Session]
    Last Profile = ''
    Auto-Save Interval = 5
    Number of Backups = 15

    [Files]
    ; For this section the user sets the key as the file name and the value as the file's directory for the file.
    ; This section is left blank by default.
    Phone Numbers = C:/Users/PC/Desktop/phone#.txt  ; The user must add the file name to the end of the URL directory.
    """
    _config = ConfigParser()
    _config.optionxform = str
    documents_dir = getenv('USERPROFILE') + '\\Documents'   # C:/Users/<User_Name>/Documents
    bm_dir = documents_dir + '\\Seize Backup Manager'   # C:/Users/<User_Name>/Documents/Seize Backup Manager
    config_dir = bm_dir + '\\config.ini'    # C:/Users/<User_Name>/Documents/Seize Backup Manager/config.ini

    def __init__(self):
        try:
            self._config.read(self.config_dir)
            # Keys and values for section [Last Session] in 'config.ini'.
            self.lastSessionKeys = [keys for keys in self._config[self._config.sections()[0]]]
            self.lastSessionValues = [self._config[self._config.sections()[0]][keys]
                                      for keys in self._config[self._config.sections()[0]]]
            # Keys and values for section [Files] in 'config.ini'. This section is used for custom files.
            self.filesKeys = [keys for keys in self._config[self._config.sections()[1]]]
            self.filesValues = [self._config[self._config.sections()[1]][keys]
                                for keys in self._config[self._config.sections()[1]]]
        except IndexError:
            # __init__() objects are created after 'config.ini' is created.
            self.create_config()
            self.__init__()

    def files(self):
        """Returns section [Files] from 'config.ini' as a dictionary."""
        return dict(zip(self.filesKeys, self.filesValues))

    def create_config(self):
        """Creates 'config.ini' file in 'Seize Backup Manager' folder at C:/Users/<User_Name>/Documents.
        Return 'None' If folder and file already exist."""
        if path.isfile(self.config_dir) is True:
            return
        if path.isdir(self.bm_dir) is False:
            mkdir(self.bm_dir)
        if path.isfile(self.config_dir) is False:
            self._config['Last Session'] = {'Last Profile': '',
                                            'Auto-Save Interval': 5,
                                            'Number of Backups': 15}
            self._config['Files'] = {}

            with open(self.config_dir, 'w') as create_config:
                self._config.write(create_config)
                create_config.close()

    def update_config(self, profile, interval, backups):
        """Update 'config.ini' with 'Select Profile', 'Interval in Min(s)' and '# of Backups' from 'BackupManager.py."""
        self._config.set(self._config.sections()[0], self.lastSessionKeys[0], profile)
        self._config.set(self._config.sections()[0], self.lastSessionKeys[1], interval)
        self._config.set(self._config.sections()[0], self.lastSessionKeys[2], backups)
        with open(self.config_dir, 'w') as update_config:
            self._config.write(update_config)
            update_config.close()

    def add_file(self, file, fpath):
        """Creates a new property and value for section '[Files]' in 'config.ini'."""
        self._config.set(self._config.sections()[1], file, fpath)
        with open(self.config_dir, 'w') as add_config:
            self._config.write(add_config)
            add_config.close()

    def remove_file(self,  option):
        """Removes a property and value for section '[Files]' in 'config.ini'"""
        self._config.remove_option(self._config.sections()[1], option)
        with open(self.config_dir, 'w') as delete_option:
            self._config.write(delete_option)
            delete_option.close()
