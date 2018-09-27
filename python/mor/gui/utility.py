# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

class Color():

	good = '#c4df9b'
	bad = '#f6989d'
	intermediate = '#fff79a'
	blank = '#f2f1f0'

	wrong = [bad,intermediate]
	color = [good,bad,intermediate,blank]

def msg_warning(msg,info):
    msg.append("WARNING    "+info)
def msg_info(msg,info):
    msg.append("INFO       "+info)
def msg_error(msg,info):
    msg.append("ERROR      "+info)
def setBackColor(widget,color=Color.intermediate):
    widget.setStyleSheet('QLineEdit { background-color: %s }' % color)

def setCellColor(tab,dialog,row,column):
    backgrdColor = QtGui.QColor()
    if dialog.state:
        backgrdColor.setNamedColor(Color.good)
        tab.item(row,column).setBackgroundColor(backgrdColor)
    else:
        backgrdColor.setNamedColor(Color.intermediate)
        tab.item(row,column).setBackgroundColor(backgrdColor)

def check_state(sender):
    # sender.blockSignals(True)

    print("check_state -------> "+str(sender.text()))
    validator = sender.validator()
    state = validator.validate(sender.text(), 0)[0]
    if state == QtGui.QValidator.Acceptable:
        color = Color.good 
    elif state == QtGui.QValidator.Intermediate:
        color = Color.intermediate
    else:
        color = Color.bad
    setBackColor(sender,color)
    # sender.blockSignals(False)


def checkedBoxes(checkBox,items,checked=True):
    '''
    checkedBoxes will with the state of a checkBox 
    change accordingly the state of other checkBoxes
    '''
    if checkBox.isChecked():
        for item in items:
            item.setCheckState(not checked)
    else:
        for item in items:
            item.setCheckState(checked)

def greyOut(checkBox,items,checked=True):
    '''
    greyOut makes items unavailable for the user by greying them out
    '''
    if type(checkBox).__name__ == 'QCheckBox':
        if checkBox.isChecked():
            for item in items:
                item.setDisabled(not checked)
        else:
            for item in items:
                item.setDisabled(checked)

    elif type(checkBox).__name__ == 'QPushButton':
        for item in items:
            # state = item.isEnabled()
            item.setDisabled(not checked)

def openFileName(hdialog,filter="Sofa Scene (*.py *.pyscn)",display=None):
    '''
    openFileName will pop up a dialog window allowing the user to choose a file
    and potentially display the path to it 
    '''
    filename = QtGui.QFileDialog.getOpenFileName(None, hdialog, '.',filter=filter)
    if display:
        display.setText(filename)       

    return filename

def openFilesNames(hdialog,display=None):
    '''
    openFilesNames will pop up a dialog window allowing the user to choose multiple files
    and potentially display there coreponding path
    '''
    filesName = QtGui.QFileDialog.getOpenFileNames(None,hdialog, '.', filter="*.stl *.vtu *.vtk")
    if display:
        for fileName in filesName:
            display.append(fileName)
    return filesName

def openDirName(hdialog,display=None):
    '''
    openDirName will pop up a dialog window allowing the user to choose a directory
    and potentially display the path to it 
    '''
    filename = QtGui.QFileDialog.getExistingDirectory(None,hdialog)
    if display:
        display.setText(filename)
    return filename

def checkExistance(dir):

    if not os.path.exists(os.path.dirname(dir)):
        try:
            os.makedirs(os.path.dirname(dir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def setAnimationParamStr(cell,items):
    tmp = ''
    for label,lineEdit in items:
        tmp +=str(label)+'='+str(lineEdit)+','
    cell.setText(tmp[:-1])

def removeLine(tab,rm=False):
    currentRow = tab.currentRow()
    rowCount = tab.rowCount()-1

    if currentRow != -1:
        rm = True 
        row = currentRow
    elif rowCount != -1:
        rm = True
        row = rowCount

    if rm:
        tab.removeRow(row)
        return row
