# This Python file uses the following encoding: utf-8

from os import error
import os.path
from time import sleep, strftime

from .utility_helper import (
    get_encoding,
    check_path
)

class LogManager(object):

    """
    Log manager for youtube-dl

    Attributes:
        LOG_FILENAME (string): File name of the log.
        TIME_TEMPLATE (string): Custom template to log the time.
        MAX_LOGSIZE (int): Maximum size (bytes) of the log file

    ArgsL
        config_path (string): Absolte the path where Logmanager shoult
        store the log file.
        add_time (boolean): If True Logmanager will also log the time.

    """
    LOG_FILENAME    = 'ytblog1000.csv'
    TIME_TEMPLATE   = '[{time}] {message}'
    #TIME_TEMPLATE   = "%(asctime)s: %(message)s"
    MAX_LOGSIZE     = 524288 #bytes ~0.5Mb
    LOG_FILEPATH    = 'D:/QtProject/YoutubeDLGui/'

    def __init__(self, config_path, add_time=False):
        self.config_path = self.LOG_FILEPATH
        self.add_time = add_time
        self.log_file = os.path.join(self.config_path, self.LOG_FILENAME)
        self._encoding = get_encoding()
        self._init_log()
        self._auto_clear_log()

        

    def OutputLog(self, data):
        # Log data to the file
        # Args: 
        #   data (string): string to write the log file
        # 
        if isinstance(data, str):
            self._write(data + '\n', 'a')         

    def _write(self, data, mode):
        """Write data to the log file.

        That's the main method for writing to the log file.

        Args:
            data (string): String to write on the log file.
            mode (string): Can be any IO mode supported by python.

        """ 
        check_path(self.LOG_FILEPATH)

        with open(self.log_file, mode) as log:
            try:
                if mode == 'a' and self.add_time:
                    msg = self.TIME_TEMPLATE.format(time=strftime('%c'), message=data)
                else:
                    msg = data

                log.write(msg)
                #log.write(msg.encode(self._encoding, 'ignore'))
            except:
                pass
                #QMessageBox.information(self, 'SelectIndexes()', strLog)

    def _log_size(self):
        # Return log file size in Bytes
        #
        if not os.path.exists(self.log_file):
            return 0
        
        return os.path.getsize(self.log_file)

    def _clear(self):
        # Clear log file.
        #
        self._write('', 'w')

    def _init_log(self):
        # Initialize the log file if not exist.
        #
        if not os.path.exists(self.log_file):
            self._write('', 'w')

    def _auto_clear_log(self):
        # Clear the log file
        #
        if self.log_file > self.LOG_FILENAME:
            self._clear()