If you have made any changes to the resources.qrc file, or haven't compiled it yet do so now using:
 pyrcc5 resources.qrc -o resources.py for PyQt5 
 or 
 pyside2-rcc resources.qrc -o resources.py for PySide2.


pyside6-uic mainwindow.ui -o MainWindow.py



pyinstaller --name="MyApplication" --windowed hello.py



https://pythonbasics.org/qt-designer-python/

https://www.mfitzp.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/