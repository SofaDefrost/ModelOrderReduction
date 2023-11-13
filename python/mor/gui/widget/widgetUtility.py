from PyQt5 import QtCore, QtGui, QtWidgets
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from mor.gui import utility as u

path = os.path.dirname(os.path.abspath(__file__))
plugin_root = path+"/../../../"
pathToIcon = path+'/../icons/'

def updatePhasesState(index,phase,phaseItem):
    '''
    Function to update the state of the other check box when one is checked.
    if user check the one from phase 4 this will automatically check the boxes of phase 1, 2 and 3

    :param items:
    :param phases:
    :param phaseItem:
    :return:
    '''
    checkBox , btn = phaseItem[index]
    phase.blockSignals(True)

    if checkBox.isChecked() == True:

        for box,btn in phaseItem[:index]:
            box.setCheckState(True)
            box.setTristate(False)

    else:
        for box,btn in phaseItem[index:]:
            box.setCheckState(False)
            box.setTristate(False)
        for box,btn in phaseItem[index:]:
            box.setDisabled(False)
            box.setTristate(False)

    phase.blockSignals(False)


def addButton(phaseWidget,grpBox_Execution):
    '''
    Utility fct to add a checkboxes and a reset button on every phase layout

    :param phaseWidget:
    :param grpBox_Execution:
    :return:
    '''

    # CheckBox
    checkBox = QtWidgets.QCheckBox(grpBox_Execution)
    checkBox.setObjectName(_fromUtf8("checkBox"))
    checkBox.setFixedWidth(30)
    checkBox.setStyleSheet("border:0px")
    checkBox.setTristate(False)

    # Reset Button
    btn = QtWidgets.QPushButton(grpBox_Execution)
    btn.setObjectName(_fromUtf8("button"))

    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(pathToIcon+'icon.png'))
    btn.setIcon(icon)
    btn.setFixedWidth(30)
    btn.setStyleSheet("border:0px")
    btn.setDisabled(True)

    phaseWidget._title_frame._hlayout.addWidget(checkBox)
    phaseWidget._title_frame._hlayout.addWidget(btn)


    return (checkBox,btn)