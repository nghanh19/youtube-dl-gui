# This Python file uses the following encoding: utf-8

import json 
import os
import logging

from .utility_helper import (
    check_path,
)

from .formats import (
    OUTPUT_FORMATS,
    FORMATS
)

class OptionsManager(object):
    """
    This clas is responsible for storing & retrieving the options.

    Args: 
        config_path (string): Absolute path where OptionsManager
            should store the settings file.

    Note:
        See load_default() method for available options.

    Example:
        Access the options using the 'options' variable.

        opt_manager = OptionsManager('.')
        opt_manager.options['save_path'] = '~/Downloads'
    """
    SETTINGS_FILENAME = 'settings.json'
    SENSITIVE_KEYS = ('sudo_password', 'password', 'video_password')    

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)


    def __init__(self, config_path):
        self.config_path = config_path
        self.settings_file = os.path.join(config_path, self.SETTINGS_FILENAME)
        self.options = dict()
        self.load_default()
        self.load_from_file()

    def load_default(self):
        """Load the default options.

        Note:
            This method is automatically called by the constructor.

        Options Description:
            'save_path' (string): Path where youtube-dl shoult store 
                the downloaded file. default is $HOME (~\Downloads)

            'save_path_dirs' (list): List that contains temporary save paths.    

            'video_format' (string): Video format to download.
                When this option is '0' youtube-dl will choose 
                the best video format for given URL.

            'second_video_format' (string): Video format to mix with the 
                one (-f 18+17)

            'to_audio' (boolean): If True youtube-dl will post process the
                video file.

            'keep_video' (boolean): If True youtube-dl will keep the video
                after post processing it.

            'audio_format' (string): Audio format of the post processed file.
                values are: mp3, wav, aac, m4a, vorbis, opus.

            'audio_quality' (string): Audio quality of the post processed file.
                values are: 9, 5, 0. The lowest value the better the quality.

            'restrict_filenames' (boolean): If True youtube-dl will restrict 
                the downloaded file filename to ASCII characters only.

            'output_format' (int): This options sets the downloaded file 
                output template. See formats.OUTPUT_FORMATS for mor info.

            'output_template' (string) : Can be any output template supported 
                by youtube-dl

            'playlist_start' (int): Playlist index to start downloading

            'playlist_end' (int): Playlist index to stop downloading.

            'max_downloads' (int): Maximun number of video files to download
                from the given playlist.

            'min_filesize' (float): Min file size of the video file.
                if the video is smaller than the given size then
                youtube-dl will abort the download process.

            'max_filesize' (float): Min file size of the video file.
                if the video is larger than the given size then
                youtube-dl will abort the download process.

            'min_filesize_unit' (string): Minimum file size unit.
                values are: '', k, m, g, y, p, e, z, y.

            'max_filesize_unit' (string): Maximum file size unit.
                values are: '', k, m, g, y, p, e, z, y.

            'write_subs' (boolean): If True youtube-dl will try to download 
                the subtitles file for the given URL.

            'write_all_subs' (boolean): If True youtube-dl will try to download
                all the available subtitles for the given URL.

            'write_auto_subs' (boolean): If True youtube-dl will try to download 
                the automatic subtitlees file for the given URL.

            'embed_subs' (boolean): If True youtube-dl will try to merge the 
                subtitles file with the video. (ONLY mp4 files)

            'subs_lang' (string): Language of the subtitles file to download.
                Needs 'write_subs' option.

            'ignore_errors' (boolean): If True youtube-dl will ignore the errors
                and continue the download process.

            'open_dl_dir' (boolean): If True youtube-dl will open the destination
                folder after download process has been completed.

            'write_description' (boolean): If True youtube-dl will the video
                description to a *.description file.

            'write_info' (boolean): If True youtube-dl will write 
                video metadata to a *.info.json file.

            'write_thumbnail' (boolean): If True youtube-dl will write a 
                thumbnail image to disk.

            'retries' (int): Number of youtube-dl retries.

            'user_agent' (string): Specify a custom user agent for youtube-dl

            'referer' (string): Specify a custom referer to user if the video
                access is restricted to one domain.

            'proxy' (string): Use the specified HTTP/HTTPS proxy.

            'shutdown' (boolean): Shutdown PC after download process completed.

            'sudo_password' (string): SUDO password for the shutdown process 
                if the user does not have elevated privileges.

            'username' (string): Username to login with.

            'password' (string): Password to login with.

            'video_password' (string): Video Password for the given URL.                        

            'youtubedl_path' (string): Absolute the path to the youtube-dl binary.
                Default is the self.config_path. You can change this position 
                to point anywhere if you want to use the youtube-dl binary on your system.
                This is also the directory where youtube-dlg will auto download the 
                youtube-dl if not exists so you should make sure you have write access 
                if you want to update the youtube-dl binary from within youtube-dlg.

            'cmd_args' (string): String that contains extra youtube-dl options 
                seperated by spaces.

            'enable_log' (boolean): If True youtube-dlg will enable 
                the LogManager, see main() function under __init__().

            'log_time' (boolean): See logmanager.LogManager add_time attribute.

            'workers_number' (int): Number of download workers that download manager 
                will spawn. Must be greater than zero.

            'locale_name' (string): Locale name (en_US)

            'main_win_size' (tuple): Main window size (width x height).
                if window becomes to small the program will reset its size.
                see _settings_are_valid method MIN_FRAME_SIZE.

            'opts_win_size' (tuple): Main window size (width x height).

            'selected_video_formats' (list): List that contains the selected
                video formats to display on the main window

            'selected_audio_formats'  (list): List that contains the selected
                audio formats to display on the main window

            'selected_format' (string): Current format selected on the main window

            'youtube_dl_debug' (boolean): When True will pass '-v' flag to youtube-dl
                config file options.

            'ignore_config' (boolean): When True will ignore youtube-dl config file option.

            'confirm_exit' (boolean): When True create message to confirm exist youtube-dlg

            'native_hls' (boolean): When True youtube-dl will use the natives HLS implementation.

            'show_completion_popup' (boolean): When True youtube-dl-dlg will create message to inform 
                the user for the download completion

            'confirm_deletion' (boolean): When True ask user before item removal.

            'nomtime' (boolean): When True will not use the last-modified header to 
                set the file modification time.

            'embed_thumbnail' (boolean): When True will embed the thumbnail in
                the audio file as cover art.

            'add_metadata' (boolean): When True will write metadata to file.         
        """

        #+++++<DEBUG_LOG>
        logging.debug("load_options default___________________")
        #-----<DEBUG_LOG>
        
        self.options = {
            'save_path' : os.path.expanduser('~'),
            'save_path_dirs': [
                os.path.expanduser('~'),
                os.path.join(os.path.expanduser('~'), "Downloads"),
                os.path.join(os.path.expanduser('~'), "Desktop"),
                os.path.join(os.path.expanduser('~'), "Videos"),
                os.path.join(os.path.expanduser('~'), "Music"),               
            ],
            'video_format': '0',
            'second_video_format': '0',
            'to_audio': False,
            'keep_video': False,
            'audio_format': '',
            'audio_quality': '5',
            'restrict_filenames': False,
            'output_format': 1,
            'output_template': os.path.join('%(uploader)s', '%(title)s.%(ext)s'),
            'playlist_start': 1,
            'playlist_end': 0,
            'max_downloads': 0,
            'min_filesize': 0,
            'max_filesize': 0,
            'min_filesize_unit': '',
            'max_filesize_unit': '',
            'write_subs': True,
            'write_all_subs': False,
            'write_auto_subs': False,
            'embed_subs': False,
            'subs_lang': 'en',
            'ignore_errors': True,
            'open_dl_dir': False,
            'write_description': False,
            'write_info': False,
            'write_thumbnail': False,
            'retries': 10,
            'user_agent': '',
            'referer': '',
            'proxy': '',
            'shutdown': False,
            'sudo_password': '',
            'username': '',
            'password': '',
            'video_password': '',
            'youtubedl_path': self.config_path,
            'cmd_args': '',
            'enable_log': True,
            'log_time': True,
            'workers_number': 3,
            'locale_name': 'en_US',
            'main_win_size': (740, 490),
            'opts_win_size': (640, 490),
            'selected_video_formats': ['default', 'mp4', 'webm'],
            'selected_audio_formats': ['mp3', 'm4a', 'vorbis'],
            'selected_format': '0',
            'youtube_dl_debug': False,
            'ignore_config': True,
            'confirm_exit': True,
            'native_hls': True,
            'show_completion_popup': True,
            'confirm_deletion': True,
            'nomtime': False,
            'embed_thumbnail': False,
            'add_metadata': False
        }

    def load_from_file(self):
        """
        Load options from settings file.
        """
        if not os.path.exists(self.settings_file):
            return
        
        with open(self.settings_file, 'rb') as settings_file:
            try:
                options = json.load(settings_file)
                
                if self._settings_coordinate(options):
                    self.options = options
            except:
                self.load_default()

    def save_to_file(self):
        """Save options to settings file.
        """
        check_path(self.config_path)

        with open(self.settings_file, 'w') as settings_file:
            options = self._get_options()
            json.dump(options,
                	  settings_file,
                	  indent=4,
                	  separators=(',', ': '))
    
    def _settings_coordinate(self, settings_dict):
        """
        Check settings.json dictionary

        Args: 
            settings_dict: Options dict loaded. See load_from_file() method.
        
        Return:
            True if settings.json is valid / else False
        """
        VALID_VIDEO_FORMAT = ('0', '17', '36', '5', '34', '35', '43', '44', '45',
            '46', '18', '22', '37', '38', '160', '133', '134', '135', '136','137',
            '264', '138', '242', '243', '244', '247', '248', '271', '272', '82',
            '83', '84', '85', '100', '101', '102', '139', '140', '141', '171', '172')

        VALID_AUDIO_FORMAT = ('mp3', 'wav', 'aac', 'm4a', 'vorbis', 'opus', '')

        VALID_AUDIO_QUALITY = ('0', '5', '9')

        VALID_FILESIZE_UNIT = ('', 'k', 'm', 'g', 't', 'p', 'e', 'z', 'y')

        VALID_SUB_LANGUAGE = ('en', 'el', 'pt', 'fr', 'it', 'ru', 'es', 'de', 'he', 'sv', 'tr')

        MIN_FRAME_SIZE = 100

        for key in self.options:
            if key not in settings_dict:
                return False

            if type(self.options[key]) != type(settings_dict[key]):
                return False

        # Check if each key has a valid value
        rules_dict = {
            'video_format': FORMATS.keys(),
            'second_video_format': VALID_VIDEO_FORMAT,
            'audio_format': VALID_AUDIO_FORMAT,
            'audio_quality': VALID_AUDIO_QUALITY,
            'output_format': OUTPUT_FORMATS.keys(),
            'min_filesize_unit': VALID_FILESIZE_UNIT,
            'max_filesize_unit': VALID_FILESIZE_UNIT,
            'subs_lang': VALID_SUB_LANGUAGE
        }

        for key, valid_list in rules_dict.items():
            if settings_dict[key] not in valid_list:
                return False

        if settings_dict['workers_number'] < 1:
            return False

        return True

    def _get_options(self):
        """
        Return options dictionary.
        """
        tmp_options = self.options.copy()

        for key in self.SENSITIVE_KEYS:
            tmp_options[key] = ''

        return tmp_options

        
        
