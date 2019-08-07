import tkinter as tk
from _tkinter import TclError
from tkinter import ttk, messagebox
from os import path, startfile
from datetime import timedelta
from contextlib import suppress
from _config import Config
from file_handler import FileHandler


class BackupManager:

    config = Config()
    countdown = None

    def __init__(self, master):
        """Widgets"""

        # Quick Save/Load Hot Keys
        root.bind("<F5>", lambda event: self.quick_save())
        root.bind("<F6>", lambda event: self.quick_load())

        self.lf_auto_save = ttk.LabelFrame(master, text='Auto-Backup')
        self.lf_auto_save.grid(row=0, column=0, padx=5, pady=0, sticky='EW')

        self.lf_auto_save_frame = tk.Frame(self.lf_auto_save)
        self.lf_auto_save_frame.grid(row=0, column=0, columnspan=25, sticky='W')

        self.profile_label = ttk.Label(self.lf_auto_save_frame, text='Select Profile:')
        self.profile_label.grid(row=0, column=0, padx=5)

        # Combobox for 'Profile Select'.
        self.profile_combo = ttk.Combobox(self.lf_auto_save_frame, width=25,
                                          values=[keys for keys in self.config.filesKeys])
        self.profile_combo.bind('<<ComboboxSelected>>', lambda arg=None: self.profile_select())
        self.profile_combo.config(state='readonly')
        self.profile_combo.grid(row=0, column=1, padx=5)

        self.dir_entry_label = ttk.Label(self.lf_auto_save_frame, text='Directory:')
        self.dir_entry_label.grid(row=0, column=2)

        # Entry box for directory URL from 'config.ini'.
        self.dir_entry_var = tk.StringVar()
        self.dir_entry = ttk.Entry(self.lf_auto_save_frame, textvariable=self.dir_entry_var, state='readonly')
        self.dir_entry.grid(row=0, column=3, padx=5)

        self.open_dir_button = ttk.Button(self.lf_auto_save_frame, text='Open Directory', command=self.open_dir)
        self.open_dir_button.grid(row=0, column=4, padx=5)

        self.lf_auto_save_frame2 = tk.Frame(self.lf_auto_save)
        self.lf_auto_save_frame2.grid(row=1, column=0, sticky='EW')

        # Start button.
        self.start_autosave = ttk.Button(self.lf_auto_save_frame2, text='Start',
                                         command=lambda: (self.listbox.insert(0, 'Auto-Backup Initiated'),
                                                          self.start_autosave.state(['disabled']),
                                                          self.stop_autosave.state(['!disabled']),
                                                          self.config.update_config(*self.update_params()),
                                                          self.start(int(self.interval_spinbox.get()) * 60)))
        self.start_autosave.grid(row=1, column=0, pady=5, padx=5, sticky='W')

        self.stop_autosave = ttk.Button(self.lf_auto_save_frame2, text='Stop', state=['disabled'],
                                        command=lambda: (self.listbox.insert(0, 'Auto-backup Stopped'),
                                                         self.stop()))
        self.stop_autosave.grid(row=1, column=1, padx=5, sticky='W')

        # Spinbox for Backup interval in minutes
        self.int_sp_var = tk.StringVar()

        self.interval_spinbox = ttk.Spinbox(self.lf_auto_save_frame2,
                                            from_=1, to=999, width=4,
                                            textvariable=self.int_sp_var)
        self.interval_spinbox.grid(row=1, column=3, padx=5, sticky='W')

        self.minutes_label = ttk.Label(self.lf_auto_save_frame2, text='Interval in Min(s):')
        self.minutes_label.grid(row=1, column=2, padx=5, sticky='W')

        # Spinbox for number of backups to save before deleting the oldest backups
        self.num_sp_var = tk.StringVar()
        self.num_spinbox = ttk.Spinbox(self.lf_auto_save_frame2, from_=0, to=999, width=4, textvariable=self.num_sp_var)
        self.num_spinbox.grid(row=1, column=5, padx=5)

        self.num_label = ttk.Label(self.lf_auto_save_frame2, text='# of Backups:')
        self.num_label.grid(row=1, column=4, padx=5, sticky='W')

        # Countdown timer which indicates time left for the next backup.
        self.timer_var = tk.StringVar()
        self.timer_var.set(timedelta(seconds=0))
        self.timer = tk.Label(self.lf_auto_save_frame2, width=8, textvariable=self.timer_var, relief='sunken')
        self.timer.config(font='System')
        self.timer.grid(row=1, column=6, padx=5)

        # Notebook for 'Data Log' and 'Edit Config' tabs.
        self.nb = ttk.Notebook(master)
        self.nb.grid(row=1, column=0, padx=5, pady=5, sticky='NSEW')

        # Frame for 'Data Log' tab.
        self.nb_frame = tk.Frame(master)
        self.nb_frame.grid(row=0, column=0, padx=5, pady=5, sticky='NSEW')
        self.nb_frame.grid_rowconfigure(1, weight=1)
        self.nb_frame.grid_columnconfigure(0, weight=1)
        self.nb.add(self.nb_frame, text='Data Log')

        self.lf_data_log = tk.Frame(self.nb_frame)
        self.lf_data_log.grid(row=0, column=0, padx=5, pady=5, sticky='EW')

        self.clear_selected_button = ttk.Button(self.lf_data_log, text='Clear', command=self.clear_selected_listbox)
        self.clear_selected_button.grid(row=0, column=0, padx=5)

        self.clear_all_button = ttk.Button(self.lf_data_log, text='Clear All', command=self.clear_all_listbox)
        self.clear_all_button.grid(row=0, column=1, padx=5)

        self.restore_button = ttk.Button(self.lf_data_log, text='Restore', command=self.restore_selected)
        self.restore_button.grid(row=0, column=2, padx=5)

        self.delete_button = ttk.Button(self.lf_data_log, text='Delete', command=self.delete_selected)
        self.delete_button.grid(row=0, column=3, padx=5)

        self.delete_all_button = ttk.Button(self.lf_data_log, text='Delete All', command=self.delete_all)
        self.delete_all_button.grid(row=0, column=4, padx=5)

        self.display_backups = ttk.Button(self.lf_data_log, text='Show Backups', command=self.show_backups)
        self.display_backups.grid(row=0, column=5, padx=5)

        self.listbox = tk.Listbox(self.nb_frame, width=45, height=25, bg='black', fg='limegreen',
                                  selectbackground='purple')
        self.listbox.grid(row=1, column=0, padx=5, pady=5, sticky='NSEW')

        # Main frame for 'Edit Config' tab.
        self.nb_frame2 = tk.Frame(master)
        self.nb_frame2.grid(row=0, column=0, padx=5, pady=5, sticky='NSEW')
        self.nb_frame2.grid_columnconfigure(0, weight=1)
        self.nb.add(self.nb_frame2, text='Edit Config')

        self.lf_config = ttk.LabelFrame(self.nb_frame2, text='Add File')
        self.lf_config.grid(row=0, column=0, padx=5, pady=5, sticky='EW')

        self.add_file_label = ttk.Label(self.lf_config, text='File Name:')
        self.add_file_label.grid(row=0, column=0, padx=5, pady=5)

        self.add_file_entry = ttk.Entry(self.lf_config)
        self.add_file_entry.grid(row=0, column=1)

        self.path_label = ttk.Label(self.lf_config, text='Path:')
        self.path_label.grid(row=0, column=2, padx=5, pady=5)

        self.path_entry = ttk.Entry(self.lf_config, width=36)
        self.path_entry.grid(row=0, column=3)

        self.add_file_button = ttk.Button(self.lf_config, text='Add File',
                                          command=lambda: (
                                              self.config.update_config(*self.update_params()),
                                              self.add_config(),
                                              self.listbox.insert(
                                                  0, f"Added '{self.add_file_entry.get()}' to 'config.ini'")))
        self.add_file_button.grid(row=0, column=4, padx=5, pady=5)

        self.lf_config2 = ttk.LabelFrame(self.nb_frame2, text='Remove File From Config')
        self.lf_config2.grid(row=1, column=0, padx=5, pady=5, sticky='EW')

        self.file_remove_label = ttk.Label(self.lf_config2, text='Select Profile:')
        self.file_remove_label.grid(row=0, column=0, padx=5, pady=5)

        self.remove_combo = ttk.Combobox(self.lf_config2, width=25, state='readonly',
                                         values=[keys for keys in self.config.filesKeys])
        self.remove_combo.grid(row=0, column=1, padx=5, pady=5)

        self.remove_file_button = ttk.Button(self.lf_config2, text='Remove File',
                                             command=lambda: (self.config.update_config(*self.update_params()),
                                                              self.remove_file(),
                                                              self.listbox.insert(
                                                                  0, f"File '{self.remove_combo.get()}' "
                                                                  f"removed from 'config.ini'")))
        self.remove_file_button.grid(row=0, column=2, padx=5, pady=5)

    def remove_file(self):
        """Get selected file from 'remove_combo.get()' and remove it from 'config.ini'."""
        self.config.remove_file(self.remove_combo.get())
        self.config.__init__()
        self.profile_combo.config(values=[keys for keys in self.config.filesKeys])
        self.remove_combo.config(values=[keys for keys in self.config.filesKeys])

    def last_session(self):
        """Sets queries for 'Select Profile', 'Directory', 'Interval in Min(s)', and '# of Backups'."""
        self.profile_combo.set(self.config.lastSessionValues[0])
        self.int_sp_var.set(self.config.lastSessionValues[1])
        self.num_sp_var.set(self.config.lastSessionValues[2])

        if self.profile_combo.get() in self.config.filesKeys:
            self.dir_entry_var.set(path.split(self.config.files()[self.profile_combo.get()])[0])
        else:
            self.dir_entry_var.set('Directory Not Found')

    def add_config(self):
        """Adds a custom file to 'config.ini'."""
        self.config.add_file(self.add_file_entry.get(), self.path_entry.get())
        self.config.__init__()
        self.profile_combo.config(values=[keys for keys in self.config.filesKeys])
        self.remove_combo.config(values=[keys for keys in self.config.filesKeys])

    def update_params(self):
        return self.profile_combo.get(), self.interval_spinbox.get(), self.num_spinbox.get()

    def profile_select(self):
        """Updates 'config.ini' and sets 'Directory' in accordance to 'Select Profile'."""
        self.config.update_config(*self.update_params())
        if self.profile_combo.get() in self.config.filesKeys:
            self.dir_entry_var.set(path.split(self.config.files()[self.profile_combo.get()])[0])
            self.listbox.insert(0, f"Profile Selected: {self.profile_combo.get()}")
        else:
            self.dir_entry_var.set('Directory Not Found')

    def open_dir(self):
        """Opens directory URL in File Explorer for directory URL in 'Directory'."""
        try:
            if len(self.dir_entry.get()) != 0:
                startfile(self.dir_entry.get())
        except FileNotFoundError:
            self.listbox.insert(0, 'Directory does not exist')

    def clear_selected_listbox(self):
        """Clears selected item from 'listbox'."""
        with suppress(TclError):
            self.listbox.delete(self.listbox.curselection())

    def clear_all_listbox(self):
        """Clears all items from 'listbox'."""
        self.listbox.delete(0, self.listbox.size())

    def restore_selected(self):
        """Restores selected backup file from 'listbox'."""
        length_of_file = len(FileHandler(self.config.files()[self.profile_combo.get()]).file_name) + 22
        try:
            file_name = self.listbox.get(self.listbox.curselection())[-length_of_file:]
            if file_name in FileHandler(self.config.files()[self.profile_combo.get()]).backup_files:
                FileHandler(self.config.files()[self.profile_combo.get()]).restore_backup(file_name)
                self.listbox.insert(0, f'File Restore: {file_name}')
        except TclError:
            self.listbox.insert(0, 'File not selected')

    def delete_selected(self):
        """Deletes selected backup file from 'listbox'."""
        length_of_file = len(FileHandler(self.config.files()[self.profile_combo.get()]).file_name) + 22
        try:
            file_name = self.listbox.get(self.listbox.curselection())[-length_of_file:]
            if file_name in FileHandler(self.config.files()[self.profile_combo.get()]).backup_files:
                FileHandler(self.config.files()[self.profile_combo.get()]).delete_backup(file_name)
                self.listbox.insert(0, f'FIle Deleted: {file_name}')
        except TclError:
            self.listbox.insert(0, 'File not selected')

    def delete_all(self):
        """Deletes all backup files from 'Backups' folder."""
        msg = messagebox.askokcancel('Warning!', 'Are you sure you want to delete all backup files?')
        if msg:
            FileHandler(self.config.files()[self.profile_combo.get()]).delete_all_backups()
            self.listbox.insert(0, 'All Backup Files Deleted')

    def show_backups(self):
        """Displays backup files to the listbox."""
        try:
            for backup_files in FileHandler(self.config.files()[self.profile_combo.get()]).backup_files:
                self.listbox.insert(0, backup_files)
        except OSError:
            self.listbox.insert(0, 'Directory does not exist.')

    def start(self, count):
        """"Initiate Auto-Backup."""
        self.timer_var.set(timedelta(seconds=count))
        if count == 0:
            self.listbox.insert(0, f"Backup file created: "
                                   f"{FileHandler(self.config.files()[self.profile_combo.get()]).backup_file()}")
            FileHandler(self.config.files()[self.profile_combo.get()]).delete_excess(int(self.num_spinbox.get()))

            count += (int(self.int_sp_var.get()) * 60) + 1
        self.countdown = root.after(1000, self.start, count - 1)

    def stop(self):
        """"Stop Auto-Backup and reset states and variables."""
        with suppress(ValueError):
            root.after_cancel(self.countdown)
        self.start_autosave.state(['!disabled'])
        self.stop_autosave.state(['disabled'])
        self.timer_var.set(timedelta(seconds=0))
        self.countdown = None

    def quick_save(self):
        FileHandler(self.config.files()[self.profile_combo.get()]).quick_save()
        self.listbox.insert(0, "Quick Save Created")

    def quick_load(self):
        FileHandler(self.config.files()[self.profile_combo.get()]).quick_load()
        self.listbox.insert(0, "Quick Save Loaded")


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Seize Backup Manager')
    with suppress(TclError):
        root.iconbitmap('icon/save_icon.ico')

    root.configure(padx=2.5, pady=2.5)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    BackupManager(root).last_session()

    root.update()
    sw = root.winfo_screenwidth() / 2
    sh = root.winfo_screenheight() / 2
    w = root.winfo_width() / 2
    h = root.winfo_height() / 2
    root.geometry('+%d+%d' % (sw - w, sh - h))

    root.mainloop()
