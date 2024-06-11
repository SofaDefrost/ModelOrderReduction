# -*- coding: utf-8 -*-
'''
**Widget used to be able to create easily Form Dialog Box**
'''

import os, sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QRegExp
# from PyQt5.QtCore import QString # --> doesn't exist anymore will return string

from collections import OrderedDict

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../')

import utility as u

# try:
#     _fromUtf8 = QString.fromUtf8
# except AttributeError:
#     def _fromUtf8(s):
#         return s
def _fromUtf8(s):
    return s

class GenericDialogForm(QDialog):
    def __init__(self,animation,param,currentValues=None,heightFields = 35,heightMargin = 10,maxWidth = 1000):
        QDialog.__init__(self)

        self.state = False
        self.animation = animation
        self.param = param
        self.row = OrderedDict()
        if not currentValues:
            self.currentValues = {}

        self.heightFields = heightFields
        self.heightMargin = heightMargin
        self.maxWidth = maxWidth

        self.resize(int(self.maxWidth/3),self.heightFields+self.heightMargin)

        self.setWindowTitle(self.animation)
        self.setupUi(self)
        self.btn_submit.clicked.connect(self.submitclose)

    def setupUi(self, ShowGroupWidget):
        self.setObjectName(_fromUtf8("Animation Parameters"))
        self.formLayout_2 = QtWidgets.QFormLayout(self)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))

        i = 0
        for attribute , value in self.param.items():
            # print(attribute,value,value[1][1])
            label = QtWidgets.QLabel(self)
            label.setObjectName(_fromUtf8("label_"+str(i)))
            label.setText(attribute)
            if value[1][1] == bool:
                widget = QtWidgets.QCheckBox(self)
                widget.setObjectName(_fromUtf8("checkBox_"+(str(i))))
                widget.setCheckState(value[0])
            else:
                widget = QtWidgets.QLineEdit(self)
                widget.setObjectName(_fromUtf8("lineEdit_"+(str(i))))
                # Validator
                widget.textChanged.emit(widget.text())
                widget.textChanged.connect(lambda: u.check_state(self.sender()))

                if type(value[1][0]) == str:
                    widget.setValidator(QtGui.QRegExpValidator(QRegExp("^("+value[1][0]+")$")))
                else:
                    widget.setValidator(value[1][0])

                # Default value
                widget.setText(str(value[0]))

                u.check_state(widget)

            self.row[label] = widget
            self.formLayout_2.setWidget(i, QtWidgets.QFormLayout.LabelRole, label)
            self.formLayout_2.setWidget(i, QtWidgets.QFormLayout.FieldRole, widget)
            i += 1

        self.btn_submit = QtWidgets.QPushButton(self)
        self.btn_submit.setObjectName(_fromUtf8("btn_submit"))
        self.btn_submit.setText("Ok")
        self.formLayout_2.setWidget(i, QtWidgets.QFormLayout.FieldRole, self.btn_submit)

        self.setFixedHeight((len(self.param)+1)*self.heightFields+self.heightMargin)
        self.setMaximumWidth(self.maxWidth)
        self.setMinimumWidth(self.width())


        self.setCurrentValues()

    def submitclose(self):
        #do whatever you need with self.roiGroups
        self.setCurrentValues()
        self.accept()

    def load(self,data):
        if data:
            for label,widget in self.row.items():
                labelTitle = str(label.text())
                dataType = self.param[labelTitle][1][1]

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
            self.setCurrentValues()

    def setCurrentValues(self):
        for label,widget in self.row.items():
            labelTitle = str(label.text())
            dataType = self.param[labelTitle][1][1]

            if dataType == bool:
                if widget.isChecked():
                    state = True
                else:
                    state = False
                self.currentValues[label.text()] = state
            else:
                if widget.text() == "":
                    print("MISSING VALUE :  for entry "+label.text()+" of "+str(dataType))
                else:
                    self.currentValues[label.text()] = dataType(widget.text())

        self.setState()

    def setState(self):
        if all( widget.palette().color(QtGui.QPalette.Background).name() not in u.Color.wrong for label,widget in self.row.items()):
            self.state = True
        else:
            self.state = False