from os import mkdir, path, remove, stat, walk
from shutil import copyfile
from time import localtime, strftime, time


class FileHandler:

    def __init__(self, fpath):
        self.fpath = fpath
        self.file_path, self.file_name = path.split(fpath)
        self.current_dt = strftime("%Y-%m-%d %H:%M:%S", localtime(int(time()))).replace(':', '꞉')
        try:
            self.backup_files = next(walk(self.file_path + '\\Backups'))[2]
        except StopIteration:
            self.create_backup_folder()
            self.__init__(fpath)

    def create_backup_folder(self):
        """Creates a path for backup files and quick saves."""
        if path.isdir(self.file_path + '\\Backups\\Quick-Save') is False:
            mkdir(self.file_path + '\\Backups')
            mkdir(self.file_path + '\\Backups\\Quick-Save')
        return

    def backup_file(self):
        """Creates a 'Backups' folder within the source file's root directory. Copies are created with a time stamp and
        placed inside the 'Backups' folder"""
        self.create_backup_folder()
        copyfile(self.fpath, self.file_path + '\\Backups\\' + self.date_stamp())
        return self.date_stamp()

    def delete_all_backups(self):
        """Deletes all backup files in 'Backups' folder."""
        for backup_file in self.backup_files:
            remove(self.file_path + '\\Backups\\' + backup_file)

    def restore_backup(self, file):
        """Override and restore source file with backup file."""
        self.create_backup_folder()
        copyfile(self.file_path + '\\Backups\\' + file, self.fpath)

    def delete_backup(self, file):
        """Deletes specific backup file from 'Backups' folder"""
        self.create_backup_folder()
        remove(self.file_path + '\\Backups\\' + file)

    def quick_save(self):
        """Creates a backup file with no timestamp in 'Quick-Save' folder."""
        self.create_backup_folder()
        copyfile(self.fpath, self.file_path + '\\Backups\\Quick-Save\\' + self.file_name)

    def quick_load(self):
        """Override and restore source file with backup file from 'Auto-Save' folder"""
        self.create_backup_folder()
        copyfile(self.file_path + '\\Backups\\Quick-Save\\' + self.file_name, self.fpath)

    def delete_excess(self, max_files):
        """The parameter, 'max_backup_files', sets the max number of backup files. Files will be deleted by oldest
        modification date if they exceed the maximum. If 'max_backup_files' is set to '0' no files will be deleted."""
        if max_files == 0:
            return
        dir_epoch = [stat(self.file_path + '\\Backups\\' + backup_file).st_mtime for backup_file in self.backup_files]
        sorted_backup_files = list(sorted(zip(self.backup_files, dir_epoch), key=lambda x: x[1]))

        # Deletes oldest files if they exceed the number passed within the 'maximum' parameter.
        while len(sorted_backup_files) > max_files:
            remove(self.file_path + '\\Backups\\' + sorted_backup_files[0][0])
            del sorted_backup_files[0]
            if len(sorted_backup_files) == max_files:
                return

    def date_stamp(self):
        """Adds date and time to backup file name."""
        if self.check_extension() is True:
            file_name, file_extension = self.get_extension(filename=True)
            return file_name + ' [' + self.current_dt + ']' + file_extension
        return self.file_name + '[' + self.current_dt + ']'

    def check_extension(self):
        """Checks for file extension. Returns None if directory does not contain any files."""
        file_name = path.splitext(self.fpath)[1]
        if path.isfile(self.fpath) is True:
            if len(path.splitext(file_name)) != 0:
                return True
            return False
        return None

    def get_extension(self, filename=False):
        """Returns the file extension. Returns both file name and extension as a list if 'filename' is set to True."""
        if self.check_extension() is True:
            if filename is True:
                return list(path.splitext(self.file_name))
            return path.splitext(self.file_name)[1]
        return None
