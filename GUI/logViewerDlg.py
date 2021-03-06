from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from UI.logViewerDlg import Ui_Dialog
import os.path

class logViewerDlg( QDialog ):
    def __init__(self, parent=None):
        super( logViewerDlg, self ).__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint |
        QtCore.Qt.WindowType.WindowTitleHint)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.download = False

        self.ui.BrowserBtn.clicked.connect(self.browser_clicked)
        self.ui.CloseBtn.clicked.connect(self.close)
        self.ui.AddBtn.clicked.connect(self.add_clicked)

    def browser_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select *.csv file", filter=str("*.csv")
        )

        if file_name == '': 
            return
            
        with open( file_name, 'r' ) as file_data:
            for line in file_data.readlines():
                self.ui.UrlsList.append(line.strip())

    def add_clicked(self):
        if str(self.ui.UrlsList.toPlainText()).strip() == '': 
            QMessageBox.information(self, 'Error!', 'Leave me the fucking urls!!!')
            return
        else:
            self.download = True
            self.close()
            
    def load(self, log_file):
        if not os.path.exists(log_file):
            QMessageBox.information(self, 'Error!', 'File not found!!!')

        with open( log_file, 'r' ) as file_data:
            for line in file_data.readlines():
                self.ui.UrlsList.append(line.strip())