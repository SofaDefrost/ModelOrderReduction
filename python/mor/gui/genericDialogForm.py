# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from collections import OrderedDict
import utility as u

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class GenericDialogForm(QtGui.QDialog):
    def __init__(self,animation,param,currentValues=None,height = 137,width = 300):
        QtGui.QDialog.__init__(self)

        self.state = False
        self.animation = animation
        self.param = param
        self.row = OrderedDict()
        if not currentValues:
            self.currentValues = {}

        self.resize(width, height)
        self.setWindowTitle(self.animation)
        self.setupUi(self)
        self.btn_submit.clicked.connect(self.submitclose)

    def setupUi(self, ShowGroupWidget):
        self.setObjectName(_fromUtf8("Animation Parameters"))
        self.formLayout_2 = QtGui.QFormLayout(self)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))

        i = 0
        for attribute , value in self.param.iteritems():
            label = QtGui.QLabel(self)
            label.setObjectName(_fromUtf8("label_"+str(i)))
            label.setText(attribute)
            if value[1] == bool:
                widget = QtGui.QCheckBox(self)
                widget.setObjectName(_fromUtf8("checkBox_"+(str(i))))
            else:
                widget = QtGui.QLineEdit(self)
                widget.setObjectName(_fromUtf8("lineEdit_"+(str(i))))
                # Validator
                widget.textChanged.emit(widget.text())
                widget.textChanged.connect(lambda: u.check_state(self.sender()))

                if type(value[0]) == str:
                    widget.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^("+value[0]+")$")))
                else:
                    widget.setValidator(value[0])

            u.setBackColor(widget)

            self.row[label] = widget
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.LabelRole, label)
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.FieldRole, widget)
            i += 1

        self.btn_submit = QtGui.QPushButton(self)
        self.btn_submit.setObjectName(_fromUtf8("btn_submit"))
        self.btn_submit.setText("Ok")
        self.formLayout_2.setWidget(i, QtGui.QFormLayout.FieldRole, self.btn_submit)

        self.setFixedHeight(self.height()) 
        self.setMaximumWidth(1000)
        self.setMinimumWidth(self.width())


    def submitclose(self):
        #do whatever you need with self.roiGroups
        self.setCurrentValues()
        self.accept()

    def load(self,data):
        if data:
            for label,widget in self.row.iteritems():
                labelTitle = str(label.text())
                dataType = self.param[labelTitle][1]

                if dataType == bool:
                    if data[str(label.text())]:
                        widget.setCheckState(bool(data[labelTitle]))
                    else:
                        widget.setCheckState(False)
                else:
                    if data[str(label.text())] != None:
                        widget.setText(str(data[labelTitle]))
                    else:
                        widget.setText('')
        else:
            for label,widget in self.row.iteritems():
                if dataType == bool:
                    widget.setCheckState(False)
                else:
                    widget.setText('')

        self.setCurrentValues()

    def setCurrentValues(self):
        for label,widget in self.row.iteritems():
            labelTitle = str(label.text())
            dataType = self.param[labelTitle][1]

            if dataType == bool:
                if widget.isChecked():
                    state = True
                else:
                    state = False
                self.currentValues[label.text()] = state
            else:
                self.currentValues[label.text()] = dataType(widget.text())

        self.setState()

    def setState(self):
        if all( widget.palette().color(QtGui.QPalette.Background).name() not in u.Color.wrong for label,widget in self.row.iteritems()):
            self.state = True
        else:
            self.state = False