from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QTimer, pyqtProperty

class ColorLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(ColorLabel, self).__init__(parent)
        self._border_color = QtGui.QColor(0, 0, 0, 0)

    def get_border_color(self):
        return self._border_color

    def set_border_color(self, color):
        self._border_color = color
        self.update()

    border_color = pyqtProperty(QtGui.QColor, get_border_color, set_border_color)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(self._border_color, 10)
        painter.setPen(pen)
        painter.drawRect(5, 5, self.width() - 10, self.height() - 10)