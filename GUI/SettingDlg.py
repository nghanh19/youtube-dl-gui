import os.path

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from UI.settingDlg import Ui_SettingDlg

from Threads.formats import (
    OUTPUT_FORMATS,
    VIDEO_FORMATS,
    AUDIO_FORMATS
)


class SettingDlg( QDialog ):

    # Lang code
    LOCATE_NAMES = {
        'ar_SA'	: 'Arabic',
        'en_US'	: 'English',
        'ko_KR'	: 'korean',
        'pt_BR'	: 'Portuguese',
        'ru_RU'	: 'Russian',
        'es_ES'	: 'Spanish',        
    }

    # Output template
    OUTPUT_TEMPLATES = [
        'Id', 
        'Title',
        'Ext',
        'Uploader',
        'Resolution',
        'Autonumer',
        '',
        'View Count',
        'Like Count',
        'Dislike Count',
        'Comment Count',
        'Average Rating',
        'Age Limit',
        'Width',
        'Height',
        'Extractor',
        '',
        'Playlist',
        'Playlist Index'
    ]

    def __init__(self, parent=None):
        super( SettingDlg, self ).__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint |
        QtCore.Qt.WindowType.WindowTitleHint)

        self.ui = Ui_SettingDlg()
        self.ui.setupUi(self)

        self.opt_manager = parent.opt_manager
        self.log_manager = parent.log_manager
        self.app_icon = None

        self._was_shown = False

        self.GeneralTab = self.ui.General
        self.FormatsTab = self.ui.Formats
        self.DownloadsTab = self.ui.Downloads
        self.AdvancedTab = self.ui.Advanced
        self.ExtraTab = self.ui.Extra

        self.tabs = (
            (self.GeneralTab, "General"),
            (self.FormatsTab, "FormatsTab"),
            (self.DownloadsTab, "Downloads"),
            (self.AdvancedTab, "Advanced"),
            (self.ExtraTab, "Extra")
        )

        # self.tabsheet = QTabWidget()
        # for tab, label in self.tabs:
        #     self.tabsheet.addTab(tab, label)

        self.ui._closeBtn.clicked.connect(self.close)
        self.ui._resetBtn.clicked.connect(self.on_reset)

        self.ui.language_combobox.activated.connect(self._on_language)
        self.ui.filename_format_combobox.currentTextChanged.connect(self._on_filename_format)
        
        # Attach menu items to a push button
        self._menu = QMenu(self)

        self.load_all_options()

    def on_close(self, event):
        self.save_all_options()
        # I still don't know how to callback parent
        #self.GetParent()._update_videoformat_combobox()
        self.hide()

    def on_reset(self, event):
        self.reset()
        #self.GetParent().reset()

    def reset(self):
        self.opt_manager.load_default()
        self.load_all_options()

    def _on_language(self):
        QMessageBox.information(self, 
                                'Information', 
                                'In order for the changes to take effect please restart', 
                                QMessageBox.Ok)

    def _on_filename_format(self):
        custom_selected = self.ui.filename_format_combobox.currentText() == OUTPUT_FORMATS[3]
        
        self.ui.filename_custom_edit.setEnabled(custom_selected)
        self.ui.filename_custom_btn.setEnabled(custom_selected)

    def _on_template(self, menu_item):
        QMessageBox.information(self, 
                        'Information', 
                        'Context menu {0}'.format(menu_item), 
                        QMessageBox.Ok) 

    def load_all_options(self):
        # General tab
        #

        # Language combobox
        for index, item in enumerate(self.LOCATE_NAMES.items()):
            _, lang_name = item
            self.ui.language_combobox.insertItem(index, lang_name)
        self.ui.language_combobox.setCurrentText(self.LOCATE_NAMES[self.opt_manager.options['locale_name']])

        # Filename format combobox
        for index, item in enumerate(OUTPUT_FORMATS.items()):
            _, filename_format = item
            self.ui.filename_format_combobox.insertItem(index, filename_format)
        self.ui.filename_format_combobox.setCurrentText(OUTPUT_FORMATS[self.opt_manager.options['output_format']])

        # Filenam format custom
        self.ui.filename_custom_edit.setText(self.opt_manager.options['output_template'])
        self.ui.filename_custom_btn.setMenu(self._menu)
        self.add_menu(self.OUTPUT_TEMPLATES, self._menu)

        self.ui.filename_ascii_checkbox.setChecked(self.opt_manager.options['restrict_filenames'])
        self.ui.confirm_exit_checkbox.setChecked(self.opt_manager.options['confirm_exit'])
        self.ui.confirm_deletion_checkbox.setChecked(self.opt_manager.options['confirm_deletion'])
        self.ui.download_completion_checkbox.setChecked(self.opt_manager.options['show_completion_popup'])
        self.ui.shutdown_completion_checkbox.setChecked(self.opt_manager.options['shutdown'])

    def add_menu(self, menu_item, menu_obj):
        if isinstance(menu_item, list):
            for item in menu_item:
                self.add_menu(item, menu_obj)
        else:
            action = menu_obj.addAction(menu_item)
            action.triggered.connect(lambda:self._on_template(menu_item))
            action.setIconVisibleInMenu(False)
            

    def save_all_options(self):
        self.opt_manager.options['locale_name'] = self.LOCATE_NAMES[self.ui.language_combobox.currentText()]
        self.opt_manager.options['output_format'] = OUTPUT_FORMATS[self.ui.filename_format_combobox.currentText()]
        self.opt_manager.options['output_template'] = self.ui.filename_custom_edit.text()
        self.opt_manager.options['restrict_filenames'] = self.ui.filename_ascii_checkbox.isChecked()
        self.opt_manager.options['confirm_exit'] = self.ui.confirm_exit_checkbox.isChecked()
        self.opt_manager.options['confirm_deletion'] = self.ui.confirm_deletion_checkbox.isChecked()
        self.opt_manager.options['show_completion_popup'] = self.ui.shutdown_completion_checkbox.isChecked()
        self.opt_manager.options['shutdown'] = self.ui.shutdown_completion_checkbox.isChecked()

    def show(self, *args, **kwargs):
        if not self._was_shown:
            self._was_shown = True

        self.showNormal()

class GeneralTab(object):
    pass

class FormatsTab(object):
   pass

class DownloadsTab(object):
   pass

class AdvancedTab(object):
   pass

class ExtraTab(object):
   pass