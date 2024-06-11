import os
from PyQt5 import QtCore , QtWidgets , QtGui
from PyQt5.QtWidgets import QLineEdit


path = os.path.dirname(os.path.abspath(__file__))
pathToIcon = path+'/../icons/'

class LineEdit(QLineEdit):
    '''

    '''

    clicked = QtCore.pyqtSignal() # signal when the text entry is left clicked
    focused = QtCore.pyqtSignal() # signal when the text entry is focused
    leftArrowBtnClicked = QtCore.pyqtSignal(bool)

    def __init__(self, value):

        super(LineEdit, self).__init__(value)

        self.leftArrowBtn = QtWidgets.QToolButton(self)
        self.leftArrowBtn.setIcon(QtGui.QIcon(pathToIcon+'leftArrow.png'))
        self.leftArrowBtn.setStyleSheet('border: 0px; padding: 0px;')
        self.leftArrowBtn.setCursor(QtCore.Qt.ArrowCursor)
        self.leftArrowBtn.clicked.connect(self.leftArrowBtnClicked.emit)
        self.leftArrowBtn.resize(12,12)

        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        leftArrowBtnSize = self.leftArrowBtn.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (leftArrowBtnSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), leftArrowBtnSize.width() + frameWidth*2 - 2),
                            max(self.minimumSizeHint().height(), leftArrowBtnSize.height() + frameWidth*2 + 2))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: self.clicked.emit()
        else: super().mousePressEvent(event)

    def focusInEvent(self,event):
        super(LineEdit, self).focusInEvent(event)
        self.focused.emit()

    def resizeEvent(self, event):
        buttonSize = self.leftArrowBtn.sizeHint()
        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.leftArrowBtn.move(self.rect().right() - frameWidth - buttonSize.width() + 5,int(
                         (self.rect().bottom() - buttonSize.height() + 10 )/2))

        super(LineEdit, self).resizeEvent(event)