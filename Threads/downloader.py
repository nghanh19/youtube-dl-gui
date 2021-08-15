# This Python file uses the following encoding: utf-8
""" YoutubeDlg module for managing the download process.

This module is responsible for managing the download process 
and update the GUI interface.

Attributes:
	MANAGER_PUB_TOPIC (string): Publisher subcription topic of the 
		DownloadManager thread.
		
	WORKER_PUB_TOPIC (string): Publisher subcription topic of the
		Worker thread.
		
Notes:
	It's not the actual module that download the Urls
	that's the job of the 'downloaders' module.
	
"""

from PyQt5.QtCore import (
    Qt, QObject, QThread, pyqtSignal
)

from logging import FATAL, log
import time
import os 
import json

from os import pipe
import queue
import sys
import signal
import subprocess

from threading import (
    Thread,
)

from .utility_helper import (
    get_encoding,
)

#+++++<DEBUG_LOG>
import logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
#-----<DEBUG_LOG>

class PipeReader(Thread):
    """ Helper class to avoid deadlocks when reading from subprocess pipes

    This class uses python threads and message queues in order to read from subprocess

    Attributes:
        WAIT_TIME (float): Time in seconds to sleep

    Args:
        queue (queue.Queue): Python queue to store the output of the subprocess    
    """

    WAIT_TIME = 0.1

    def __init__(self, queue):
        super(PipeReader, self).__init__()
        self._filedescriptor = None
        self._running = True
        self._queue = queue

        self.start()

    def run(self):
        # Flag to ignore specific lines
        ignore_line = False

        while self._running:
            if self._filedescriptor is not None:
                for line in iter(self._filedescriptor.readline, ''):
                    # Ignore ffmpeg stderr
                    #line = line.decode(self._encoding, 'ignore')
                    if str('ffmpeg version') in line:
                        ignore_line = True

                    if not ignore_line:
                        self._queue.put_nowait(line)
                        #+++++<DEBUG_LOG>
                        #logging.debug("_filedescriptor=%s", line)
                        #-----<DEBUG_LOG>    

                self._filedescriptor = None
                ignore_line = False

            time.sleep(self.WAIT_TIME)

    def attach_filedescriptor(self, filedesc):
        # Attach a filedescriptor to the PipeReader
        #
        self._filedescriptor = filedesc

    def join(self, timeout=None):
        self._running = False
        super(PipeReader, self).join(timeout)


class YoutubeDLDownloader(object):
    """
    Python class for downloading videos using youtube-dl and processing

    Attributes:
        OK, ERROR, STOPPED, ALREADY, FILISIZE_ABORT, WARNING (int): Integers
            that describe the return code from the download() method. The
            larger the number of the higher is the hierarchy of the code.
            Codes with smaller hierarchy cannot overwrite codes with higher
            hierarchy.

    Args:
        youtubedl_path (string): Absolute path to youtube-dl binary.

        data_hook (function): Optional callback function to retrieve download
            process data.

        log_data (function): Optional callback function to write data to
            the log file.

    Warnings:
        The caller is responsible for calling the close() method after he has
        finished with the object in order for the object to be able for properly
        close down itself.

    Example:
        How to use YoutubeDlDownloader from a python script:

        from downloadmanager import YoutubeDLDownloader

        def data_hook(data):
            print(data)

        downloader = YoutubeDLDownloader('/usr/bin/youtube-dl', data_hook)

        downloader.download(<URL_STRING>, ['-f, 'flv])

    """

    OK = 0
    WARNING = 1
    ERROR = 2
    FILESIZE_ABORT = 3
    ALREADY = 4
    STOPPED = 5

    def __init__(self, youtubedl_path, data_hook=None, log_data=None):
        self.youtubedl_path = youtubedl_path
        self.data_hook = data_hook
        self.log_data = log_data

        self._ret_code = self.OK
        self._proc = None

        #self._encoding = get_encoding()
        self._encoding = get_encoding()
        self._stderr_queue = queue.Queue() #the queue size is infinite.
        self._stderr_reader = PipeReader(self._stderr_queue)

    def download(self, url, options):
        """Download url using given options.

        Args:
            url (string): 
            options (list): youtube-dl options

        Ret:
            Status of the download process
            There are 6 situalsions ret code.

            OK = The download process completed
            WARNING = A warning occured during download process
            ERROR = A error occured during download process
            FILESIZE_ABORT = The corresponding url video file was larger or
                smaller from the given filesize limit.
            ALREADY = The given url already downloaded.
            STOPPED = The download process was stopped by the USER.

        """
        #logging.info("___YoutubeDLDownloader_________")

        self._ret_code = self.OK

        cmd = self._get_cmd(url, options)
        self._create_process(cmd)

        self._stderr_reader.attach_filedescriptor(self._proc.stderr)

        while self._proc_is_alive():
            stdout = self._proc.stdout.readline().rstrip()
            #stdout = stdout.decode(self._encoding, 'ignore')

            if stdout:
                data_dict = extract_data(stdout)
                #self._extract_info(data_dict)
                self._hook_data(data_dict)

        # Read stderr after download process has been completed
        # We don't need to read stderr in real time
        while not self._stderr_queue.empty():
            
            #logging.info("not stderr_queue.empty()")  

            stderr = self._stderr_queue.get_nowait().rstrip()
            #stderr = stderr.decode(self._encoding, 'ignore')

            self._log(stderr)

            if self._is_warning(stderr):
                self._set_retcode(self.WARNING)
            else:
                self._set_retcode(self.ERROR)

        self._last_data_hook()

        return self._ret_code

    def _is_warning(self, stderr):
        return stderr.split(':')[0] == 'WARNING'        

    def stop(self):
        # Stop the download process and set return code to stopped
        #
        if self._proc_is_alive():
            if os.name == 'nt':
                # os.killpg is not available on Windows
                # see https://bugs.python.org/issue5115

                logging.info("___._proc.kill()_______")
                self._proc.kill()
            else:
                os.killpg(self._proc.pid, signal.SIGKILL)

            self._set_retcode(self.STOPPED)

    def close(self):
        # Blocks until all items in the queue have been gotten and processed.
        self._stderr_reader.join()

    def _set_retcode(self, code):
        # if the given code is higher than the current self._ret_code
        #
        if code >= self._ret_code:
            self._ret_code = code

    def _log(self, data):
        # Log data using the callback function
        #
        if self.log_data is not None:
            self.log_data(data)
            
    def _hook_data(self, data):
        # Pass data back to the caller
        #
        if self.data_hook is not None:
            self.data_hook(data)

    def _last_data_hook(self):

        #logging.info("______._last_data_hook()_______")

        """Set the last data info based on the return code
        """
        data = {}
        if self._ret_code == self.OK:
            data['status'] = 'Finished'
        elif self._ret_code == self.ERROR:
            data['status'] = 'Error'
            data['speed'] = ''
            data['eta'] = ''
        elif self._ret_code == self.WARNING:
            data['status'] = 'Warning'
            data['speed'] = ''
            data['eta'] = ''
        elif self._ret_code == self.STOPPED:
            data['status'] = 'Stopped'
            data['speed'] = ''
            data['eta'] = ''        
        elif self._ret_code == self.ALREADY:
            data['status'] = 'Already Downloaded'
        else:
            data['status'] = 'Filesize Abort'  

        self._hook_data(data)

    def _create_process(self, cmd):
        """Create new process

        Args: 
            cmd (list): python list the contains the command the execute.

        """ 
        info = preexec = None
        if os.name == 'nt':
            # Hie subprocess window
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            # Make subprocess the process group leader
            # in order to kill the whole process group with os.killpg
            preexec = os.setsid

        # Encode command for subprocess
        # refer to http://stackoverflow.com/a/9951851/35070
        if sys.version_info < (3, 0):
            cmd = [item.encode(self._encoding, 'ignore') for item in cmd]

        self._proc = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      preexec_fn=preexec,
                                      startupinfo=info,
                                      text=True,
                                      encoding=get_encoding(),
                                      shell=True )    
    
    def _proc_is_alive(self):
        # Return True if self._proc is alive / else False
        #
        if self._proc is None:
            return False

        return self._proc.poll() is None

    def _get_cmd(self, url, options): 
        """Build the subprocess command

        Args:
            url (string): 
            options (list): youtube-dl options

        Ret:
            python list that contains the command the execute

        """

        if os.name == 'nt':
            cmd = [self.youtubedl_path] + options + [url]
        else:
            cmd = ['python', self.youtubedl_path] + options + [url]
        
        logging.info("_get_cmd(%s)", cmd)

        return cmd


def extract_data(stdout):
    """Extract data from youtube-dl stdout.

    Args:
        stdout (string): Contains the youtube-dl stdout.

    Ret:
        python dict: The returned dict can be empty if there are
        no data to extract eslt it may contrain one of more of the
        following keys:

        status: contains the status of the process download.
        path: destination path
        extension: the file extension
        filenme: the file name with out ext
        percent: the percentage of the video being downloaded.
        eta: estimate time for the completion of the download process.
        speed: download speed
        filesize: the size of the video file being downloaded
        playlist_index: the playlist index of the current video file being downloaded
        playlist_size: the number of vides in the playlist


    """ 
    # REFACTOR
    def extract_filename(input_data):
        path, fullname = os.path.split(input_data.strip("\""))
        filename, extension = os.path.splitext(fullname)

        return path, filename, extension

    data_dictionary = {}

    if not stdout:
        return data_dictionary

    # We want to keep the spaces in order to extract filenames with
    # multiple whitespaces correctly. We also keep a copy of the old 
    # 'std' for backward compatibility with the old code
    # Output template example
    # stdout = "[download]   1.9% of 4.30GiB at  1.01MiB/s ETA 01:11:25"

    stdout_with_spaces = stdout.split(' ')
    stdout = stdout.split()

    #+++++<DEBUG_LOG>
    logging.debug("%s", stdout)
    #-----<DEBUG_LOG>

    stdout[0] = stdout[0].lstrip('\r')

    if stdout[0] == '[download]':
        data_dictionary['status'] = 'Downloading'

        # Get path, filename & ext
        if stdout[1] == 'Destination:':
            path, filename, extension = extract_filename(' '.join(stdout_with_spaces[2:]))

            data_dictionary['path'] = path
            data_dictionary['filename'] = filename
            data_dictionary['extension'] = extension

        # Get progress info
        if '%' in  stdout[1]:
            if stdout[1] == '100%':
                data_dictionary['status'] = 'Already Downloaded'
                data_dictionary['filesize'] = stdout[3]
                data_dictionary['percent'] = '100%'
                data_dictionary['eta'] = ''
                data_dictionary['speed'] = ''
            else:
                data_dictionary['percent'] = stdout[1]
                data_dictionary['filesize'] = stdout[3]
                data_dictionary['speed'] = stdout[5]
                data_dictionary['eta'] = stdout[7]

        # Get playlist info (if exist)
        if stdout[1] == 'Downloading' and stdout[2] == 'video':
            data_dictionary['playlist_index'] = stdout[3]
            data_dictionary['playlist_size'] = stdout[5]

        # Remove the 'and merged' part from stdout when using ffmpeg to merge the formats
        if stdout[-3] == 'downloaded' and stdout [-1] == 'merged':
            stdout = stdout[:-2]
            stdout_with_spaces = stdout_with_spaces[:-2]

            data_dictionary['percent'] = '100%'

        # Get file already downloaded status
        if stdout[-1] == 'downloaded':
            data_dictionary['status'] = 'Already Downloaded'
            path, filename, extension = extract_filename(' '.join(stdout_with_spaces[1:-4]))

            data_dictionary['path'] = path
            data_dictionary['filename'] = filename
            data_dictionary['extension'] = extension

        # Get filesize abort status
        if stdout[-1] == 'Aborting.':
            data_dictionary['status'] = 'Filesize Abort'

    elif stdout[0] == '[hlsnative]':
        # native hls extractor
        # see: https://github.com/rg3/youtube-dl/blob/master/youtube_dl/downloader/hls.py#L54
        data_dictionary['status'] = 'Downloading'

        if len(stdout) == 7:
            segment_no = float(stdout[6])
            current_segment = float(stdout[4])

            # Get the percentage
            percent = '{0:.1f}%'.format(current_segment / segment_no * 100)
            data_dictionary['percent'] = percent

    elif stdout[0] == '[ffmpeg]':
        data_dictionary['status'] = 'Post Processing'

        # Get final extension after merging process
        if stdout[1] == 'Merging':
            path, filename, extension = extract_filename(' '.join(stdout_with_spaces[4:]))

            data_dictionary['path'] = path
            data_dictionary['filename'] = filename
            data_dictionary['extension'] = extension

        # Get final extension ffmpeg post process simple (not file merge)
        if stdout[1] == 'Destination:':
            path, filename, extension = extract_filename(' '.join(stdout_with_spaces[2:]))

            data_dictionary['path'] = path
            data_dictionary['filename'] = filename
            data_dictionary['extension'] = extension    

        # Get final extension after recoding process
        if stdout[1] == 'Converting':
            path, filename, extension = extract_filename(' '.join(stdout_with_spaces[8:]))

            data_dictionary['path'] = path
            data_dictionary['filename'] = filename
            data_dictionary['extension'] = extension

    elif stdout[0][0] != '[' or stdout[0] == '[debug]':
        pass  # Just ignore this output

    else:
        data_dictionary['status'] = 'Pre Processing'

    return data_dictionary