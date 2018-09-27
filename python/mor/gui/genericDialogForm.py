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
            lineEdit = QtGui.QLineEdit(self)
            lineEdit.setObjectName(_fromUtf8("lineEdit_"+(str(i))))

            # Validator 
            lineEdit.textChanged.emit(lineEdit.text())
            lineEdit.textChanged.connect(lambda: u.check_state(self.sender()))
            lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^("+value[0]+")$")))
            u.setBackColor(lineEdit)

            self.row[label] = lineEdit
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.LabelRole, label)
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.FieldRole, lineEdit)
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
        for label,lineEdit in self.row.iteritems():
            if data:
                if data[str(label.text())]:
                    lineEdit.setText(data[str(label.text())])
                else:
                    lineEdit.setText('')
            else:
                lineEdit.setText('')

        self.setCurrentValues()

    def setCurrentValues(self):
        for label,lineEdit in self.row.iteritems():
            self.currentValues[label.text()] = lineEdit.text()
            self.setState()

    def setState(self):
        if all( lineEdit.palette().color(QtGui.QPalette.Background).name() not in u.Color.wrong for label,lineEdit in self.row.iteritems()):
            self.state = True