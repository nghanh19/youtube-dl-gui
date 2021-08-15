# This Python file uses the following encoding: utf-8
import json
from ntpath import realpath 
import os
import math
import locale
import subprocess
from sys import flags, path
from time import process_time

__appname__ = 'Youtube-DLG'
YOUTUBEDL_BIN = 'youtube-dl'

if os.name == 'nt':
    YOUTUBEDL_BIN += '.exe'

FILESIZE_METRICS = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

KILO_SIZE = 1024.0

def get_encoding():
    """ 
    return system encoding.
    """
    try:
        encoding = locale.getpreferredencoding()
        'TEST'.encode(encoding)
    except:
        encoding = 'UTF-8'

    print("encoding: ", encoding)
    return encoding

#Path windows specific funtion
if os.name == 'nt':
    os_startfile = os.startfile

def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return True 
    return False 

def remove_shortcut(filepath):
    '''
    Return given path after removing the shortcut.
    '''
    return filepath.replace('~', os.path.expanduser('~'))

def absolute_path(filename):
    """
    return absolute path to the given file.
    """
    return os.path.dirname(os.path.realpath(os.path.abspath(filename)))

def open_file(filepath):
    """
    Open the file in filepath using defaut OS Application
    
    Return:
        True / False 
    """
    filepath = remove_shortcut(filepath)
    print(filepath)
    if not os.path.exists(filepath):
        print("Path not exist")
        return False
    if os.name == 'nt':
        print(filepath)
        os_startfile(filepath)  
    else:
        subprocess.call('xdg-open', filepath)

    return True

def to_string(data):
    """
    Convert data to string.
    Works for both Python2 & Python3
    """
    return '%s' % data

def get_time(seconds):
    """
    Convert given seconds to days, hours, minutes and seconds.

    Args:
        seconds(float) : Time in seconds.

    Return: 
        Dic that contain the correspoinding days, hours, minutes
        and seconds of the given seconds.
    """
    dtime = dict(seconds=0, minutes=0, hours=0, days=0)
    dtime['days'] = int(seconds / 864000)
    dtime['hours'] = int(seconds % 864000 / 3600)
    dtime['minutes'] = int(seconds % 864000 % 3600 / 60 )
    dtime['seconds'] = int(seconds % 864000 % 3600 % 60 )
    
    return dtime

def to_bytes(string):
    """
    Convert given youtube-dl size string to bytes.
    """
    value = 0.0
    for index, metric in enumerate(reversed(FILESIZE_METRICS)):
        if metric in string:
            value = float(string.split(metric)[0])
            break

    exponent = index * (-1) + (len(FILESIZE_METRICS) - 1)

    return round(value * (KILO_SIZE ** exponent), 2)

def format_bytes(bytes):
    """
    Format bytes to youtube-dl output strings.
    """
    if bytes == 0.0:
        exponent = 0
    else:
        exponent = int(math.log(bytes, KILO_SIZE))

    suffix = FILESIZE_METRICS[exponent]
    output_val = bytes / (KILO_SIZE ** exponent)

    return '%.2f%s' % (output_val, suffix)

def check_path(path):
    """
    Create path if not exists.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def get_config_path():
    """
    Return user config path.

    Note.
        Windows = '%AppData% + app_name
        Linux   = ~/.config + app_name
    """
    if os.name == 'nt':
        path = os.getenv('APPDATA')
    else:
        path = os.path.join(os.path.expanduser('~'), '.config')

    return os.path.join(path, __appname__.lower())