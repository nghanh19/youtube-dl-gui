# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Project\youtube_dl_Gui\YoutubeDLGui\UI\resources\logViewerDlg.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(945, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.UrlsList = QtWidgets.QTextEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.UrlsList.setFont(font)
        self.UrlsList.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.UrlsList.setReadOnly(True)
        self.UrlsList.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.UrlsList.setObjectName("UrlsList")
        self.verticalLayout.addWidget(self.UrlsList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BrowserBtn = QtWidgets.QPushButton(Dialog)
        self.BrowserBtn.setObjectName("BrowserBtn")
        self.horizontalLayout.addWidget(self.BrowserBtn)
        spacerItem = QtWidgets.QSpacerItem(318, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.AddBtn = QtWidgets.QPushButton(Dialog)
        self.AddBtn.setObjectName("AddBtn")
        self.horizontalLayout.addWidget(self.AddBtn)
        self.CloseBtn = QtWidgets.QPushButton(Dialog)
        self.CloseBtn.setObjectName("CloseBtn")
        self.horizontalLayout.addWidget(self.CloseBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.UrlsList.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.BrowserBtn.setText(_translate("Dialog", "Browser"))
        self.AddBtn.setText(_translate("Dialog", "Add"))
        self.CloseBtn.setText(_translate("Dialog", "Close"))
