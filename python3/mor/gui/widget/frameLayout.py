# -*- coding: utf-8 -*-
'''
**Widget used to have a foldable GroupBox**
'''
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget

class Communicate(QtCore.QObject):

    clicked = QtCore.pyqtSignal()

class FrameLayout(QWidget):
    '''
    '''

    def __init__(self, parent=None, title=None):
        QtWidgets.QFrame.__init__(self, parent=parent)
        self._is_collasped = True
        self.collapsed = False
        self._title_frame = None
        self._content, self._content_layout = (None, None)

        # self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self._main_v_layout = QtWidgets.QVBoxLayout(self)
        # self._main_v_layout.setSizeConstraint(QtGui.QLayout.SetMaximumSize) #QtGui.QLayout.SetFixedSize)

        self._main_v_layout.addWidget(self.initTitleFrame(title, self._is_collasped))
        self._main_v_layout.addWidget(self.initContent(self._is_collasped))

        self.initCollapsable()
        # print("HEIGHT = "+str(self.height()))
        # print("WIDTH = "+str(self.width()))

    def title(self):
        return self._title_frame._title.text()

    def setObjectName(self,name):
        QWidget.setObjectName(self,name)
        self._title_frame.setObjectName("title") #+self.objectName())
        self._main_v_layout.setObjectName("vlayoutMain") #+self.objectName())
        self._content_layout.setObjectName("vlayoutContent") #+self.objectName())
        self._content.setObjectName("content") #+self.objectName())

    def initTitleFrame(self, title, collapsed):
        self._title_frame = self.TitleFrame(title=title, collapsed=collapsed)

        return self._title_frame

    def initContent(self, collapsed):
        self._content = QWidget()
        # self._content.resize(500, 30)
        self._content_layout = QtWidgets.QVBoxLayout()

        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)

        return self._content

    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def initCollapsable(self):
        # QtCore.QObject.connect(self._title_frame, QtCore.SIGNAL('clicked()'), self.toggleCollapsed)
        self._title_frame.c.clicked.connect(self.toggleCollapsed)

    def toggleCollapsed(self):
        self._is_collasped = not self._is_collasped
        # print('toggleCollapsed ------------------> '+str(self._is_collasped))
        self._content.setVisible(not self._is_collasped)
        # print('-----------------------> there')
        self.collapsed = not self.collapsed
        self._title_frame._arrow.setArrow(int(self._is_collasped))

        # print("HEIGHT = "+str(self.height()))
        # print("WIDTH = "+str(self.width()))

    def sizeHint(self):
        height = 0
        defaultHeight = 30
        margin = 15

        if not self._is_collasped :
            # print("Not Collapse")
            for child in self.children():
                # print(type(child).__name__)
                if type(child).__name__ == 'TitleFrame' or type(child).__name__ == 'QWidget':
                    height += child.height()
        else :
            # print("default")
            height = defaultHeight
        # print("--------------> sizeHint "+str(self._title_frame._title.text())+" :\n    width : "+str(self.window().width())+' height : '+str(height))
        size = QtCore.QSize(self.window().width()-margin,height)
        return size

    ############################
    #           TITLE          #
    ############################
    class TitleFrame(QtWidgets.QFrame):
        def __init__(self, parent=None, title="", collapsed=False):
            QtWidgets.QFrame.__init__(self, parent=parent)
            # self.resize(500, 24)

            self.setMinimumHeight(24)
            self.setMaximumHeight(24)
            self.move(QtCore.QPoint(24, 0))
            self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

            self._hlayout = QtWidgets.QHBoxLayout(self)
            self._hlayout.setContentsMargins(0, 0, 0, 0)
            self._hlayout.setSpacing(0)

            self._arrow = None
            self._title = None

            self._hlayout.addWidget(self.initArrow(collapsed))
            self._hlayout.addWidget(self.initTitle(title))

            self.c = Communicate()

        def setObjectName(self,name):
            QWidget.setObjectName(self,name)
            self._hlayout.setObjectName("hlayout") #+self.objectName())
            self._arrow.setObjectName("arrow")
            self._title.setObjectName("title")

        def initArrow(self, collapsed):
            self._arrow = FrameLayout.Arrow(collapsed=collapsed)
            self._arrow.setStyleSheet("border:0px")

            return self._arrow

        def initTitle(self, title=None):
            self._title = QtWidgets.QLabel(title)
            self._title.setMinimumHeight(24)
            self._title.move(QtCore.QPoint(24, 0))
            self._title.setStyleSheet("border:0px")

            return self._title

        def mousePressEvent(self, event):
            # self.emit(QtCore.SIGNAL('clicked()'))
            # return super(FrameLayout.TitleFrame, self).mousePressEvent(event)

            self.c.clicked.emit()


    #############################
    #           ARROW           #
    #############################
    class Arrow(QtWidgets.QFrame):
        def __init__(self, parent=None, collapsed=False):
            QtWidgets.QFrame.__init__(self, parent=parent)

            self.setMaximumSize(24, 24)

            # horizontal == 0
            self._arrow_horizontal = (QtCore.QPointF(7.0, 8.0), QtCore.QPointF(17.0, 8.0), QtCore.QPointF(12.0, 13.0))
            # vertical == 1
            self._arrow_vertical = (QtCore.QPointF(8.0, 7.0), QtCore.QPointF(13.0, 12.0), QtCore.QPointF(8.0, 17.0))
            # arrow
            self._arrow = None
            self.setArrow(int(collapsed))

        def setArrow(self, arrow_dir):
            if arrow_dir:
                self._arrow = self._arrow_vertical
            else:
                self._arrow = self._arrow_horizontal

        def paintEvent(self, event):
            painter = QtGui.QPainter()
            painter.begin(self)
            painter.setBrush(QtGui.QColor(192, 192, 192))
            painter.setPen(QtGui.QColor(64, 64, 64))
            painter.drawPolygon(*self._arrow)
            painter.end()