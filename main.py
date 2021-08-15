# This Python file uses the following encoding: utf-8
from math import log
import os
import sys
from pathlib import Path
from threading import Thread, Timer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import concurrent.futures

from GUI import *
from GUI.AboutDlg import AboutDialog
from GUI.logViewerDlg import logViewerDlg
from GUI.SettingDlg import SettingDlg
from UI.gui_qtdesigner import Ui_MainFrameWnd

import UI.resource_rc
import logging
import clipboard


from pubsub import pub as Subcriber

from Threads.downloadmanager import (
    MANAGER_PUB_TOPIC,
    WORKER_PUB_TOPIC,
    DownloadManager,
    DownloadList,
    DownloadItem,
)

from Threads.parsers import (
    OptionHolder,
    OptionsParser
)

from Threads.logmanager import (
    LogManager
)

__PACKAGENAME__ = 'youtube_dl_gui'
WAIT_TIME = 0.1

from Threads.optionsmanager import OptionsManager

from Threads.utility_helper import (
    open_file,
    get_config_path,
    #get_locale_file,
    __appname__
)

WAIT_TIME = 0.1

# Set config path and create options and log managers
config_path = get_config_path()
opt_manager = OptionsManager(config_path)
log_manager = LogManager(config_path, True)

'''
if opt_manager.options['enable_log']:
    log_manager = LogManager(config_path, opt_manager.options['log_time'])
'''


# Setting custom variables
downloads_dir = str(Path.home() / "Downloads")
try:
    app_root = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    app_root = os.path.dirname(os.path.abspath(sys.argv[0]))


class MainFrameWnd(QMainWindow):
    """
    Main window class.
    This class is responsible for creating the main app window
    and binding the events.
    """

    """
    column_key: (column_number, column_label, minimum_width, is_resizable)
    """

    DOWNLOAD_STARTED = "Downloads started"
    STOP_LABEL  = "Stop"
    START_LABEL  = "Start"

    CLOSING_MSG = "Stopping downloads"
    CLOSED_MSG = "Downloads stopped"

    VIDEO_LABEL = "Title"
    EXTENSION_LABEL = 'Extension'
    SIZE_LABEL = 'Size'
    PERCENT_LABEL = 'Percent'
    ETA_LABEL = 'ETA'    
    SPEED_LABEL = 'Speed'
    STATUS_LABEL = "Status"

    IDLE = 0
    RUNNING = 1
    ERROR = 2

    URL_REPORT_MSG = "Total progress: {0:.1f}% | Queue({1} | Paused ({2}) | Active ({3}) | Completed ({4}) | Error ({5})"

    LIST_COLUMNS = {
        'filename' : (0, VIDEO_LABEL, 400, True),
        'extension': (1, EXTENSION_LABEL, 69, True),
        'filesize':  (2, SIZE_LABEL, 100, True),
        'percent':   (3, PERCENT_LABEL, 59, True),
        "eta":       (4, ETA_LABEL, 59, True),
        'speed':     (5, SPEED_LABEL, 90, True),
        'status':    (6, STATUS_LABEL, 108, True),
    }

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)

    # Update download list result
    update_date = pyqtSignal(int, object)

    def __init__(self, opt_manager, log_manager, parent=None):
        super(MainFrameWnd, self).__init__(parent)
        self.ui = Ui_MainFrameWnd()
        self.ui.setupUi(self)
        
        # Update UI at first START
        #
        self._resetUi()
        
        # Log manager
        #
        self.log_manager = log_manager
        # Options manager
        #
        self.opt_manager = opt_manager

        # Download manager
        #
        self.download_manager = None

        # MAIN STATE
        self.state = self.IDLE

        # Status list sheet table
        for column_item in self.LIST_COLUMNS.values():
            column = column_item[0]
            header = QTableWidgetItem( column_item[1] )
            self.ui._dl_tablewidget.setHorizontalHeaderItem(column, header)

            column_width = column_item[2]
            self.ui._dl_tablewidget.setColumnWidth(column, column_width)

            #column_resize = column_item[3]
            #if column_resize is True:
                #self.ui._dl_tablewidget.resizeColumnToContents(0)
                #self.ui._dl_tablewidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # Hook various event to their respective callbacks.
        #
        self.ui._dl_tablewidget.cellClicked.connect(self._oncellClicked)
        self.ui._dl_tablewidget.cellChanged.connect(self._oncellChanged)
        self.ui._dl_tablewidget.cellEntered.connect(self._oncellEntered)
        self.ui._dl_tablewidget.cellPressed.connect(self._oncellPressed)
        self.ui._dl_tablewidget.cellActivated.connect(self._cellActivated)

        self.update_date.connect(self._update_from_item)

        # Set the app icon
        #
        path = os.path.join(app_root, 'UI', 'images', 'icon.png')
        self.setWindowIcon(QtGui.QIcon(path))

        # Download list
        #
        self._download_list = DownloadList()

        # Set up youtube-dl option manager
        #
        self._options_parser = OptionsParser()

        # Edit - Running condition
        #
        self._setting_dlg = SettingDlg(self)

        # Set the Timer
        self._app_timer = QTimer(self)
        self._app_timer.timeout.connect(self._onTimer)

        # Download path combobox
        #
        self.ui._path_combobox.addItem("D:\\Downloads\\Test")
        #self.ui._path_combobox.addItem(self.opt_manager.options['save_path_dirs'])
        self.ui._path_combobox.setCurrentIndex(0)
        self._update_savepath(None)
       
        # Video format combobox
        #
        self.ui._videoformat_combobox.addItems(self.opt_manager.options['selected_video_formats'])   
        self.ui._videoformat_combobox.addItems(self.opt_manager.options['selected_audio_formats'])
        self.ui._videoformat_combobox.setCurrentIndex(0)

        #QApplication.clipboard().dataChanged.connect(self.clipboardchanged)

        # Set focus to Url list
        #
        self.ui._urls_list.setFocus()

        # Show status bar
        #
        self._update_status_bar('Ready.')        

        # Set threads wxCallAfter handlers
        #
        self._set_subcriber(self._download_worker_handler, WORKER_PUB_TOPIC)
        self._set_subcriber(self._download_manager_handler, MANAGER_PUB_TOPIC)
        
        self.connect_pushbtn_action()
        self.connect_menu_action()
        self.show()

    def clipboardchanged(self):
        text = QApplication.clipboard().text()
        print(text)
        self.ui._urls_list.append(text)

    def _update_status_bar(self, msg):
        # Display msg in the status bar.
        #
        self.ui.statusbar.showMessage(msg) 

    def _resetUi(self):
        # Reset GUI widgets after update or download process.
        #
        self.ui._downloadBtn.setText(self.START_LABEL)
        self.ui._downloadBtn.setToolTip(self.START_LABEL)
        path = os.path.join(app_root, 'UI', 'resources', 'start_32px.png')
        self.ui._downloadBtn.setIcon(QtGui.QIcon(path))

    def _oncellClicked(self):
        pass
        #for curItem in self.ui._dl_tablewidget.selectedItems():
        #+++++<DEBUG_LOG>
        # curItem = self.ui._dl_tablewidget.currentItem()
        # print('Clicked:', curItem.row(),
        #                   curItem.column(),
        #                   curItem.text(), 
        #                   curItem.data(curItem.row()))
                
        #curItem = self.ui._dl_tablewidget.currentItem()
        #self.ui._dl_tablewidget.removeRow(curItem.row())

        #self.ui._dl_tablewidget.setItem()
        #self._update_table_by_item(item.row(), item)
        #-----<DEBUG_LOG>

    def _oncellChanged(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            pass
            #+++++<DEBUG_LOG>
            #print('Changed:', curItem.row(),
            #curItem.column(),
            #curItem.text())
            #-----<DEBUG_LOG>

    def _oncellEntered(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            pass
            #+++++<DEBUG_LOG>
            #print('Entered:', curItem.row(),
            #curItem.column(),
            #curItem.text())
            #-----<DEBUG_LOG>

    def _oncellPressed(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            pass
            #+++++<DEBUG_LOG>
            #print('Pressed:', curItem.row(),
            #curItem.column(),
            #curItem.text())
            #-----<DEBUG_LOG>
    
    def _cellActivated(self):
        curItem = self.ui._dl_tablewidget.currentItem()
        print('Clicked:', curItem.row(),
                          curItem.column(),
                          curItem.text(), 
                          curItem.data(curItem.row())) 
        #for curItem in self.ui._dl_tablewidget.selectedItems():
        #    pass
            #+++++<DEBUG_LOG>
            #print('Activated:', curItem.row(),
            #curItem.column(),
            #curItem.text())
            #-----<DEBUG_LOG>      

    def connect_menu_action(self):
        self.ui.actionImportURL.triggered.connect(self._on_importURL)
        self.ui.actionCondition.triggered.connect(self._on_settingDlg)

        self.ui.actionExit.triggered.connect(self.closeEvent)
        self.ui.actionAbout.triggered.connect(self.showAbout)
        self.ui.actionLogViewer.triggered.connect(self.logViewer)
        self.ui.actionImportURL.triggered.connect(self._on_importURL)

    def connect_pushbtn_action(self):
        self.ui._add_btn.clicked.connect(self._on_add)

        self.ui._browser_btn.clicked.connect(self._on_savepath)
        self.ui._importurlBtn.clicked.connect(self._on_importURL)
        self.ui._deleteBtn.clicked.connect(self._on_delete)
        self.ui._downloadBtn.clicked.connect(self._on_start)
        self.ui._playBtn.clicked.connect(self._on_play)

        self.ui._arrowupBtn.clicked.connect(self._on_arrow_up)
        self.ui._arrowdownBtn.clicked.connect(self._on_arrow_down)

        self.ui._open_path.clicked.connect(self._on_open_path)

    def _on_open_path(self, event):
        open_file(self.ui._path_combobox.currentText())

    def _on_arrow_up(self, event):

        # If table is none
        row_cnt = self.ui._dl_tablewidget.rowCount()
        if row_cnt < 1:
            return

        # Selected item
        index = self.ui._dl_tablewidget.currentRow()
        if index <= 0:
            return

        # Selected download item
        object_id = self._download_list.get_objectid_by_index(index)
        download_item = self._download_list.get_item_by_objectid(object_id)

        # Swap data in download_list
        self._download_list.move_up(object_id)

        # Selected item up to 1 step (you'll see they down 1 step in real QWidgettable)
        new_index = index - 1

        self.ui._dl_tablewidget.removeRow(new_index)
        self.ui._dl_tablewidget.insertRow(new_index)
        self.ui._dl_tablewidget.selectRow(new_index)

        self._update_from_item(new_index, download_item)

        object_id = self._download_list.get_objectid_by_index(index)
        download_item = self._download_list.get_item_by_objectid(object_id)
        self.ui._dl_tablewidget.removeRow(index)
        self.ui._dl_tablewidget.insertRow(index)
        self._update_from_item(index, download_item)      

    def _on_arrow_down(self, event):

        # If table is none
        row_cnt = self.ui._dl_tablewidget.rowCount()
        if row_cnt < 1:
            return

        index = self.ui._dl_tablewidget.currentRow()

        object_id = self._download_list.get_objectid_by_index(index)
        download_item = self._download_list.get_item_by_objectid(object_id)

        new_index = index + 1
        
        if index == row_cnt - 1:
            return

        self._download_list.move_down(object_id)



        self.ui._dl_tablewidget.removeRow(new_index)
        self.ui._dl_tablewidget.insertRow(new_index)
        self.ui._dl_tablewidget.selectRow(new_index)
        
        self._update_from_item(new_index, download_item)

        object_id = self._download_list.get_objectid_by_index(index)
        download_item = self._download_list.get_item_by_objectid(object_id)

        self.ui._dl_tablewidget.removeRow(index)
        self.ui._dl_tablewidget.insertRow(index)
        self._update_from_item(index, download_item)

    def _on_start(self, event):
        if self.download_manager is None:
            self._start_download()
        else:
             self.download_manager.stop_downloads()

    def _start_download(self):
        if self.ui._dl_tablewidget.rowCount() == 0:
            QMessageBox.information(self, 
                                    'Warning', 
                                    'No items to download', 
                                    QMessageBox.Ok)

        else:
            self._startTimer()
            self.download_manager = DownloadManager(self, 
                                                    self._download_list, 
                                                    self.opt_manager, 
                                                    self.log_manager)

            self.ui._downloadBtn.setText(self.STOP_LABEL)
            self.ui._downloadBtn.setToolTip(self.STOP_LABEL)
            path = os.path.join(app_root, 'UI', 'resources', 'stop_32px.png')
            self.ui._downloadBtn.setIcon(QtGui.QIcon(path))

            self._update_status_bar(self.DOWNLOAD_STARTED)

            self.state = self.RUNNING

    def closeEvent(self, event):
        """Event handler for EVT_CLOSE event 
        
        This method is used when the user tries to close to program
        to save the options make sure that the download & update 
        processes are not running
        """

        # msgBox = QMessageBox(self)
        # msgBox.setWindowTitle("Exit")
        # #msgBox.setText("Some files are currently being downloaded.")
        # msgBox.setInformativeText("Do you really want to close?")
        # msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # msgBox.setDefaultButton(QMessageBox.Cancel)
        # ret = msgBox.exec_()      

        ret = QMessageBox.information(self, 
                                'Exit',
                                'Do you really want to close?',
                                QMessageBox.Ok | QMessageBox.Cancel, 
                                QMessageBox.Cancel)

        if ret == QMessageBox.Cancel:
            event.ignore()
        else:
            self._close()

    def _on_play(self, event):

        index = self.ui._dl_tablewidget.currentRow()
        if index == -1:
            return

        object_id = self._download_list.get_objectid_by_index(index)
        download_item = self._download_list.get_item_by_objectid(object_id)   

        if download_item.stage == 'Completed':
            if download_item.filenames:
                filename = download_item.get_files()[-1]
                open_file(filename)
        else:
            pass

    def _close(self):
        if self.download_manager is not None:
            self.download_manager.stop_downloads()
            self.download_manager.join()

        # Store options
        self.opt_manager.options['save_path_dirs'] = self.ui._path_combobox.currentText()

        #self.opt_manager.save_to_file() //<temporary comment out>

        self.close()

    def _on_delete(self, row_number=-1):
        """ Delete download item in download table

        Args:
            row_number: -1 delete all item, other delete selected row
        """

        row_cnt = len(self._download_list.get_items())

        #row_cnt = self.ui._dl_tablewidget.rowCount()
        print(row_cnt)
        if row_cnt <= 0:
            return

        index = self.ui._dl_tablewidget.currentRow()
        print(index)
        if index == -1: #if there wasn't anything selected, 1st item will be selected
            index = 0

        object_id = self._download_list.get_objectid_by_index(index)
        self._download_list.remove(object_id)
        self.ui._dl_tablewidget.removeRow(index)

    def _on_importURL(self):
        file, _ = QFileDialog.getOpenFileName( 
            self, "Select a file", filter=str('*.csv *.txt')
        )

        if file == '':
            return

        with open(file, 'r') as data:
            for line in data.readlines():
                self.ui._urls_list.append(line.strip())

    def _on_add(self, event):
        urls = self._get_urls()
        self.ui._dl_tablewidget.setRowCount(len(urls))

        if not urls:            
            QMessageBox.information(
                self,
                'Warning',
                'Leave me a fucking url!'
            )
        else:
            self.ui._urls_list.clear()
            options = self._options_parser.parse(self.opt_manager.options)         

            for row, url in enumerate(urls):
                download_item = DownloadItem(url, options)
                download_item.path = self.opt_manager.options['save_path']

                if not self._download_list.has_item(download_item.object_id):
                    self._download_list.insert(download_item)
                    self._binding_data(row, download_item)   

                    #+++++<DEBUG_LOG>
                    logging.debug("%d: %s %s",download_item.object_id, download_item.options, download_item.url)
                    #-----<DEBUG_LOG>                     

    def _binding_data(self, row, download_item):

        self._update_from_item(row, download_item)

    def _update_from_item(self, row, download_item):

        #logging.debug("_update_table_by_item {}".format(row))

        progress_stats = download_item.progress_stats

        for key, value in self.LIST_COLUMNS.items():
        #for column in self.ui._dl_tablewidget.columnCount():
            column = value[0]
            
            if key == 'status' and progress_stats['playlist_index']:
                # Not the best place but we build the playlist status here
                status = '{0} {1}/{2}'.format(progress_stats['status'],
                                              progress_stats['playlist_index'],
                                              progress_stats['playlist_size'])
                column_value = QTableWidgetItem(status)                       
            else:
                column_value = QTableWidgetItem(progress_stats[key])

            self.ui._dl_tablewidget.setItem(row, column, column_value)
            self.ui._dl_tablewidget.update()

    def _get_urls(self):
        urls = set()    # do not allow duplicate values.
        urls.update(self.ui._urls_list.toPlainText().split('\n'))
        return [url for url in urls if url]

    def showAbout(self):
        aboutDlg = AboutDialog(self)
        aboutDlg.show()

    def logViewer(self):
        if self.log_manager is None:
            QMessageBox.information(self, 'Information', 
                                    'Logging is disabled',
                                    QMessageBox.Ok)

        else:
            logViewDlg = logViewerDlg(self)
            logViewDlg.load(self.log_manager.log_file)
            logViewDlg.show()

    def _on_settingDlg(self):
        self._setting_dlg.show(self)

    def batch_file(self):
        self.batch_dialog.exec()
        if self.batch_dialog.download is True:
            urls = list(self.batch_dialog.ui.UrlsList.toPlainText().split('\n'))
            for url in urls:
                self.download_url(str(url))
        else:
            return

    def _on_savepath(self, event):
        path = QFileDialog.getExistingDirectory(self, "Select destination")
        if path == '':
            return

        self.ui._path_combobox.insertItem(0, path)
        self.ui._path_combobox.setCurrentIndex(0)
        self._update_savepath(None)

    def _update_savepath(self, event):
        self.opt_manager.options['save_path'] = self.ui._path_combobox.currentText()

    def _onTimer(self):

        if self.state == self.IDLE:
            self._stopTimer()

        total_percentage = 0.0
        queued = paused = active = completed = error = 0

        for item in self._download_list.get_items():
            if item.stage == 'Queued':
                queued += 1
            if item.stage == 'Paused':
                paused += 1
            if item.stage == 'Active':
                active += 1
                total_percentage += float(item.progress_stats["percent"].split('%')[0])
            if item.stage == 'Completed':
                completed += 1
            if item.stage == 'Error':
                error += 1

        items_count = queued + paused + active + completed + error    
        total_percentage += completed * 100.0 + error * 100.0

        if items_count:
            total_percentage /= items_count 

        msg = self.URL_REPORT_MSG.format(total_percentage, queued, paused, active, completed, error)                    
        self._update_status_bar(msg)

    def _startTimer(self):
        #logging.info("_startTimer____________")
        self._app_timer.start(100)

    def _stopTimer(self):
        #logging.info("_stopTimer____________")
        self._app_timer.stop()

    def _set_subcriber(self, data, topic):
        """Set a handler for the given topic.

        Args
            hanlder (function): Can be any function with one param 
                the message that the caller sends

            event (string): Can be any string such an event identifier the caller.
                you can Bind multiple handlers on the same topic or 
                multiple topics on the same handler
        """
        Subcriber.subscribe(data, topic)
    
    def _download_worker_handler(self, data):
        """downloadmanager.Worker thread handler.

        Handles messages from the Worker thread

        Args:
            See downloadmanager.Worker _talt_to_gui() method.
        """

        self.signal, self.data = data
        #logging.info("_download_worker_handler: {0}".format(self.signal))

        download_item = self._download_list.get_item_by_objectid(self.data['index'])
        download_item.update_status(self.data)

        row = self._download_list.index(self.data['index'])

        self.update_date.emit(row, download_item)     # transmit a signal
        time.sleep(WAIT_TIME)                         # Fired every 0.1 seconds

    def _download_manager_handler(self, data):
        """downloadmanager.DownloadManager thread handler

        Handles messages from the DownloadManager thread

        Args:
            See downloadmanager.DownloadManager _talk_to_gui()
        """
        self.data = data

        logging.info("_download_manager_handler(%s)", self.data)

        if self.data == 'finished':
            self.download_manager = None
            self._resetUi()
            self._afterDownloading()
            self.state = self.IDLE

        elif self.data == 'closed':
            self._update_status_bar(self.CLOSED_MSG)
            self._resetUi()
            self.download_manager = None
            self.state = self.IDLE
            
        elif self.data == 'closing':
            self._update_status_bar(self.CLOSING_MSG)     
        else:
            pass

    def _afterDownloading(self):
        """Run tasks after download process has been completed.

        Note:
            Here you can add any tasks you want to run after the
            download process has been completed.

        """
        # QMessageBox.information(self, 
        #                         'Information', 
        #                         'Downloads completed', 
        #                         QMessageBox.Ok)


def main():
    app = QApplication(sys.argv)
    myapp = MainFrameWnd(opt_manager, log_manager)
    myapp.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
