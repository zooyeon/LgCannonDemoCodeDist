from PyQt5 import QtCore, QtGui, QtWidgets

class NumericPlainTextEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_0, QtCore.Qt.Key_1, QtCore.Qt.Key_2, 
                           QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5, 
                           QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, 
                           QtCore.Qt.Key_9, QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete,
                           QtCore.Qt.Key_Left, QtCore.Qt.Key_Right, QtCore.Qt.Key_Home,
                           QtCore.Qt.Key_End, QtCore.Qt.Key_Tab):
            super().keyPressEvent(event)
        else:
            event.ignore()