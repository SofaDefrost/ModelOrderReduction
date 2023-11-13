# -*- coding: utf-8 -*-
'''
**Widget used to be able to create easily Form Dialog Box**
'''

import os, sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget

# Colors specifications 
from mor.gui.settings.ui_colors import * 
from mor.gui.settings import existingAnimation as anim

from mor.gui.widget import LineEdit
from mor.gui.widget import Completer
from mor.gui.widget import TreeModel
from mor.gui.widget import GenericDialogForm

from mor.gui import utility as u

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../')


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class AnimationTableWidget(QTableWidget):

    def __init__(self,value,exp_path):

        super(AnimationTableWidget, self).__init__(value)

        # Validator
        self.exp_path = exp_path

        # QTable Action
        self.cellClicked.connect(self.showAnimationDialog)
        self.animationDialog = []


        # existing Animation 
        self.existingAnimation = None 


        # currentPhase
        self.currentPhase = None


    def addLine(self,cfg,number=1,animation='defaultShaking'):
        '''
        Fct creating a new line of the animation tab widget.
        Each line is quite complex and has multiple widget integrated in it:
        - Cell 0 -> QCheckBox                    : allow to select a specific line in order to test it 
        - Cell 1 -> QComboBox                    : allow to select which animation we want, propose in a combo the different animation available defined in the file existingAnimation 
        - Cell 2 -> QDialog (GenericDialogForm)  : allow to give the argument which will be passed on the selected animation fonction thanks to what has been defined in the file existingAnimation
        - Cell 3 -> QCompleter (Completer)       : allow to choose to which object or node we want to apply this animation on.
                                                   The cell will automatically propose to choose a node/object of the graphscene of the scene we have previousle selected. 
        '''

        for new in range(number):
            self.insertRow(self.rowCount())
            row = self.rowCount()-1

            tmp = LineEdit(self)
            tmp.setReadOnly(True)

            checkBox = QtWidgets.QCheckBox()
            checkBox.setObjectName(_fromUtf8("checkBox"))
            checkBox.setFixedWidth(30)
            checkBox.setStyleSheet("border:0px")
            self.setCellWidget(row,0,checkBox)
            model = TreeModel(cfg,obj=True)

            completer = Completer(tmp)
            completer.setModel(model)
            completer.setCompletionColumn(0)
            completer.setCompletionRole(QtCore.Qt.DisplayRole)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            tmp.setCompleter(completer)

            tmp.textChanged.emit(tmp.text())
            tmp.textChanged.connect(lambda: u.check_state(self.sender()))
            tmp.setValidator(QtGui.QRegExpValidator(self.exp_path))

            tmp.clicked.connect(completer.complete)
            tmp.focused.connect(completer.complete)

            completer.activated.connect(lambda: u.display(completer))
            checkBox.stateChanged.connect(lambda: self.phaseSelected())
            checkBox.setCheckState(True)
            checkBox.setTristate(False)
            tmp.leftArrowBtnClicked.connect(lambda:  u.left(tmp))


            u.setBackColor(tmp)
            self.setCellWidget(row,3,tmp)

            item = QtWidgets.QTableWidgetItem()
            self.setItem(row,2,item)
            backgrdColor = QtGui.QColor()
            backgrdColor.setNamedColor(yellow)
            self.item(row,2).setBackground(backgrdColor)

            self.animationDialog.append(GenericDialogForm(animation,self.existingAnimation[animation]))
            self.addComboToTab(self.existingAnimation.keys(),row,1)


            self.setAnimationParamStr((row,2))
            self.setCellColor((row,2))

        self.resizeTab()


    def removeLine(self,rm=False):
        '''
        removeLine remove the current selected row or the last one created and also the associated dialog box object 
        '''
        currentRow = self.currentRow()
        rowCount = self.rowCount()-1

        if currentRow != -1:
            rm = True
            row = currentRow
        elif rowCount != -1:
            rm = True
            row = rowCount

        if rm:
            self.removeRow(row)

        if row:
            self.animationDialog.remove(self.animationDialog[row])

        self.resizeTab()


    def addComboToTab(self,values,row,column):
        '''
        addComboToTab will add a QComboBox to an QTableWidget[row][column] and fill it with different value 
        '''
        combo = QtWidgets.QComboBox()
        combo.setObjectName(_fromUtf8("combo"+str(row)+str(column)))
        combo.activated.connect(lambda: self.addAnimationDialog(row,column,column+1))
        for value in values:
            combo.addItem(value)
        self.setCellWidget(row,column,combo)


    def addAnimationDialog(self,row,column,dialogColumn):
        '''
        
        '''
        previousAnimation = self.animationDialog[row].animation
        currentAnimation = str(self.cellWidget(row,column).currentText())

        if previousAnimation != currentAnimation:
            self.animationDialog[row] = GenericDialogForm(currentAnimation,self.existingAnimation[currentAnimation])
            self.item(row,dialogColumn).setText('')


    def showAnimationDialog(self, row=None, column=None,dialog=None):
        if dialog:
            dialog.exec_()
            return
        if column == 2 :
            dialog = self.animationDialog[row]
            if dialog.exec_():
                self.setAnimationParamStr((row,column))
                self.setCellColor((row,column))


    def setAnimationParamStr(self,cell):
        row , column = cell
        item = self.item(row,column)
        items = self.animationDialog[row].currentValues.items()
        tmp = ''
        for label,lineEdit in items:
            tmp +=str(label)+'='+str(lineEdit)+','
        item.setText(tmp[:-1])


    def setCellColor(self,cell):
        row , column = cell
        dialog = self.animationDialog[row]
        backgrdColor = QtGui.QColor()
        if dialog.state:
            backgrdColor.setNamedColor(Color.good)
            self.item(row,column).setBackground(backgrdColor)
        else:
            backgrdColor.setNamedColor(Color.intermediate)
            self.item(row,column).setBackground(backgrdColor)


    def resizeTab(self):
        nbrRow = self.rowCount() #grpBox_AnimationParam.width(),grpBox_AnimationParam.height())

        defaultHeight = 34
        defaultWidth = 537
        maxWidth = 800 - (600-defaultWidth)
        sizeHeader = self.horizontalHeader().height()

        if nbrRow == 0:
            nbrRow = 1
            sizeForRow = defaultHeight
            width = defaultWidth
        else:
            sizeForRow = 31 #self.sizeHintForRow(0)
            width = self.width()
            
        if nbrRow > 5:
            nbrRow = 5

        size = QtCore.QSize(width,sizeForRow*nbrRow+sizeHeader)

        self.setMinimumSize(size)
        size.setWidth(maxWidth)
        self.setMaximumSize(size)


    def phaseSelected(self):
        updatedPhase = []
        for row in range(self.rowCount()): 
            if self.cellWidget(row, 0).isChecked():            
                updatedPhase.append(1)
            else:
                updatedPhase.append(0)
        self.currentPhase = updatedPhase
