# This Python file uses the following encoding: utf-8

import os
import sys
import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

    
class ListCtrlTblWidget(QTableWidget):
    """
    Download list control table widget.
    This class is responsible for creating Download List
    and binding the events.
    """

    VIDEO_LABEL = "Title"
    EXTENSION_LABEL = 'Extension'
    SIZE_LABEL = 'Size'
    PERCENT_LABEL = 'Percent'
    ETA_LABEL = 'ETA'    
    SPEED_LABEL = 'Speed'
    STATUS_LABEL = "Status"

    LIST_COLUMNS = {
        'filename' : (0, VIDEO_LABEL, 400, True),
        'extension': (1, EXTENSION_LABEL, 69, True),
        'filesize':  (2, SIZE_LABEL, 100, True),
        'percent':   (3, PERCENT_LABEL, 59, True),
        "eta":       (4, ETA_LABEL, 59, True),
        'speed':     (5, SPEED_LABEL, 90, True),
        'status':    (6, STATUS_LABEL, 108, True),
    }

    #+++++<HUUANH_DEBUG>
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)
    #-----<HUUANH_DEBUG>

    def __init__(self, columns, *args, **kwargs):
        super(ListCtrlTblWidget, self).__init__(*args, **kwargs)

        self.columns = columns
        self._list_index = 0
        self._url_list = set()
        self._set_columns()
    
    def _set_columns(self):
    
        # Initilizes ListCtrl QTtableWidget
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

        self.show()

    def _oncellClicked(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            #+++++<DEBUG_LOG>
            print('Clicked:', curItem.row(),
            curItem.column(),
            curItem.text())
            #-----<DEBUG_LOG>

    def _oncellChanged(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            #+++++<DEBUG_LOG>
            print('Changed:', curItem.row(),
            curItem.column(),
            curItem.text())
            #-----<DEBUG_LOG>

    def _oncellEntered(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            #+++++<DEBUG_LOG>
            print('Entered:', curItem.row(),
            curItem.column(),
            curItem.text())
            #-----<DEBUG_LOG>

    def _oncellPressed(self):
        for curItem in self.ui._dl_tablewidget.selectedItems():
            #+++++<DEBUG_LOG>
            print('Pressed:', curItem.row(),
            curItem.column(),
            curItem.text())
            #-----<DEBUG_LOG>
    
    def _cellActivated(self):

        for curItem in self.ui._dl_tablewidget.selectedItems():
            #+++++<DEBUG_LOG>
            print('Activated:', curItem.row(),
            curItem.column(),
            curItem.text())
            #-----<DEBUG_LOG>      

    def _move_up(self, row_number):
        item = self.ui._dl_tablewidget.currentItem()
        pass
    def _move_down(self, row_number):
        
        pass

    def _move_item(self, item, cur_row, new_row):
        item = self.ui._dl_tablewidget.currentItem()
        self.ui._dl_tablewidget.removeRow(cur_row)


    def _on_deleteDownloadItems(self, row_number):
        #QTableWidgetItem 
        # del_ranges = QTableWidgetItem() # QTableWidgetSelectionRange()
        # self.ui._dl_tablewidget.selectedRanges(del_ranges)

        # del_ranges.topRow()
        # del_ranges.bottomRow()

        indx_list = self.ui._dl_tablewidget.selectedRanges()
        cell = set( (idx.topRow(), idx.bottomRow(), idx.rowCount()) for idx in indx_list)

        #for index in self.ui._dl_tablewidget:
        #indx_list = self.ui._dl_tablewidget.selectedIndexes()
        #cell = set( (idx.row(), idx.column()) for idx in indx_list)
        #+++++<DEBUG_LOG>
        #strLog = "Select cell: {0}".format(cell)
        #QMessageBox.information(self, 'SelectIndexes()', strLog)

        # Temporary remove all items
        for ditem in self._download_list.get_items():
            self.ui._dl_tablewidget.removeRow(self._download_list.index(ditem.object_id))
            self._download_list.remove(ditem.object_id)

        return
        #logging.debug("Selected row: %s, column %s", index.row, index.column)
        #-----<DEBUG_LOG>  
        #for index in indx_list:
            #+++++<DEBUG_LOG>
            #logging.debug("Selected row: %s, column %s", index.row, index.column)
            #-----<DEBUG_LOG>           
            #self.ui._dl_tablewidget.removeRow(index.row)                 

    def _bind_item(self, row, download_item):

        self._update_table_by_item(row, download_item)

    def _update_table_by_item(self, row, download_item):

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

        download_item = self._download_list.get_item(self.data['index'])
        download_item.update_status(self.data)

        row = self._download_list.index(self.data['index'])

        self._update_table_by_item(row, download_item)

    def _download_manager_handler(self, data):
        """downloadmanager.DownloadManager thread handler

        Handles messages from the DownloadManager thread

        Args:
            See downloadmanager.DownloadManager _talk_to_gui()
        """
        self.data = data

        #logging.info("_download_manager_handler(%s)", self.data)

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
