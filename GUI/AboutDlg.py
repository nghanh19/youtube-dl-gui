from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from UI.AboutDlg import Ui_Dialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent, Qt.WindowType.WindowTitleHint | 
        Qt.WindowType.WindowSystemMenuHint)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.AboutCloseBtn.clicked.connect(self.close)