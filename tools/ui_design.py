# -*- coding: utf-8 -*-
###############################################################################
#            Model Order Reduction plugin for SOFA                            #
#                         version 1.0                                         #
#                       Copyright © Inria                                     #
#                       All rights reserved                                   #
#                       2018                                                  #
#                                                                             #
# This software is under the GNU General Public License v2 (GPLv2)            #
#            https://www.gnu.org/licenses/licenses.en.html                    #
#                                                                             #
#                                                                             #
#                                                                             #
# Authors: Olivier Goury, Felix Vanneste                                      #
#                                                                             #
# Contact information: https://project.inria.fr/modelorderreduction/contact   #
###############################################################################
from PyQt4 import QtCore, QtGui
import os
import sys

# MOR IMPORT
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python') # TO CHANGE

from mor.gui import FrameLayout

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

color_frame = '#fff79a'
color_mainWindow = '#f2f1f0'
color_grpBox = '#f2f1f0'

def setBackground(obj,color):
    obj.setStyleSheet("background-color: "+color+";")

class MyLineEdit(QtGui.QLineEdit,QtCore.QObject):
    clicked = QtCore.pyqtSignal() # signal when the text entry is left clicked
    focused = QtCore.pyqtSignal() # signal when the text entry is focused
    leftArrowBtnClicked = QtCore.pyqtSignal(bool)

    def __init__(self, value):

        super(MyLineEdit, self).__init__(value)

        self.leftArrowBtn = QtGui.QToolButton(self)
        self.leftArrowBtn.setIcon(QtGui.QIcon('leftArrow.png'))
        self.leftArrowBtn.setStyleSheet('border: 0px; padding: 0px;')
        self.leftArrowBtn.setCursor(QtCore.Qt.ArrowCursor)
        self.leftArrowBtn.clicked.connect(self.leftArrowBtnClicked.emit)
        self.leftArrowBtn.resize(12,12)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        leftArrowBtnSize = self.leftArrowBtn.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (leftArrowBtnSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), leftArrowBtnSize.width() + frameWidth*2 - 2),
                            max(self.minimumSizeHint().height(), leftArrowBtnSize.height() + frameWidth*2 + 2))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: self.clicked.emit()
        else: super().mousePressEvent(event)

    def focusInEvent(self,event):
        super(MyLineEdit, self).focusInEvent(event)
        self.focused.emit()

    def resizeEvent(self, event):
        buttonSize = self.leftArrowBtn.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.leftArrowBtn.move(self.rect().right() - frameWidth - buttonSize.width() + 5,
                         (self.rect().bottom() - buttonSize.height() + 10 )/2)

        super(MyLineEdit, self).resizeEvent(event)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        # MAIN WINDOW
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.MainWindow.setMinimumSize(600, 320) #290)
        self.MainWindow.setMaximumSize(800, 320)
        self.MainWindow.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        # self.MainWindow.setStyleSheet("margin: 0px; border: 2px solid green;") # padding: 20px;") # background-color:grey;

        # CENTRAL WIDGET
        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        # SCROLL AREA
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))

        self.scrollArea.setStyleSheet('QWidget#scrollArea {border: 0px;}')
        # self.scrollArea.setStyleSheet("border: 0px;") # padding: 20px;") # background-color:grey;
        self.scrollArea.setWidget(QtGui.QWidget(self.centralwidget))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMaximumSize(800,600)

        # MAIN LAYOUTS

        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        # self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)

        self.scrollArea_layout = QtGui.QVBoxLayout(self.scrollArea.widget())
        self.scrollArea_layout.setMargin(0)
        self.scrollArea_layout.setSpacing(0)
        self.scrollArea_layout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize) #QLayout.SetFixedSize)

        self.verticalLayout.addWidget(self.scrollArea) #,0, QtCore.Qt.AlignTop)

        ########    FONTS    ########

        # Title Font
        fontTitle = QtGui.QFont()
        fontTitle.setPointSize(14)
        fontTitle.setUnderline(True)

        # Label Font
        fontLabel = QtGui.QFont()
        fontLabel.setPointSize(10)
        fontLabel.setUnderline(False)

        # LineEdit Font
        fontLineEdit = QtGui.QFont()
        fontLineEdit.setPointSize(10)
        fontLineEdit.setUnderline(False)

        # Button Font
        fontButton = QtGui.QFont()
        fontButton.setPointSize(10)
        fontButton.setUnderline(False)

        # Table Font
        fontTable = QtGui.QFont()
        fontTable.setPointSize(10)
        fontTable.setUnderline(False)
        fontTable.setBold(True)
        fontTable.setWeight(75)

        # CheckBox Font
        fontCheckBox = QtGui.QFont()
        fontCheckBox.setPointSize(10)
        fontCheckBox.setUnderline(False)

        ##########################      GROUPBOX PATH     ####################################
        self.layout_path = FrameLayout(self.centralwidget,title="Path")
        self.layout_path.setObjectName('Path')

        self.groupBoxScene(fontTitle,fontLabel,fontLineEdit,fontButton)

        self.layout_path.addWidget(self.grpBox_Path)
        self.layout_path.toggleCollapsed()

        self.scrollArea_layout.addWidget(self.layout_path)


        ##########################      GROUPBOX REDUCTION PARAM     #########################
        self.layout_reductionParam = FrameLayout(self.centralwidget,title="Reduction Parameters")
        self.layout_reductionParam.setObjectName('ReductionParameters')

        self.groupBoxReductionParam(fontTitle,fontLabel,fontLineEdit,fontCheckBox)

        self.layout_reductionParam.addWidget(self.grpBox_ReductionParam)

        self.scrollArea_layout.addWidget(self.layout_reductionParam)


        ##########################      GROUPBOX ADVANCED PARAM     ##########################
        self.layout_advancedParam = FrameLayout(self.centralwidget,title="Advanced Parameter")
        self.layout_advancedParam.setObjectName('AdvancedParameter')

        self.groupBoxAdvancedParam(fontTitle,fontLabel,fontLineEdit,fontCheckBox)

        self.layout_advancedParam.addWidget(self.grpBox_AdvancedParam)
        self.scrollArea_layout.addWidget(self.layout_advancedParam) #, 0, QtCore.Qt.AlignTop)


        ##########################      GROUPBOX ANIAMATION PARAM     ########################
        self.layout_aniamationParam = FrameLayout(self.centralwidget,title="Animation Parameters")
        self.layout_aniamationParam.setObjectName('AnimationParameters')

        self.grouprBoxAnimationParam(fontTitle,fontTable,fontButton)

        self.layout_aniamationParam.addWidget(self.grpBox_AnimationParam)
        self.scrollArea_layout.addWidget(self.layout_aniamationParam) #, 0, QtCore.Qt.AlignTop)


        ##########################      GROUPBOX EXECUTION     ###############################
        self.layout_execution = FrameLayout(self.centralwidget,title="Execution")
        self.layout_execution.setObjectName('Execution')

        self.groupBoxExecution(fontTitle,fontLineEdit)

        self.layout_execution.addWidget(self.grpBox_Execution)
        self.scrollArea_layout.addWidget(self.layout_execution) #, 0, QtCore.Qt.AlignTop)


        ##########################      LAUNCH REDUCTION     #################################

        # Layout
        self.layout_launchReduction = QtGui.QGridLayout()
        self.layout_launchReduction.setObjectName(_fromUtf8("layout_launchReduction"))

        ########    CONTENTS    ########

        # Separator Line
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setObjectName(_fromUtf8("line"))

        # Button
        self.btn_launchReduction = QtGui.QPushButton(self.centralwidget)
        self.btn_launchReduction.setObjectName(_fromUtf8("btn_launchReduction"))


        # Spacer
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        ################################

        # Add Contents to Layout
        self.layout_launchReduction.addWidget(self.btn_launchReduction, 1, 1, 1, 1)
        self.layout_launchReduction.addItem(spacerItem, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.line)
        self.verticalLayout.addLayout(self.layout_launchReduction)

        ##########################      MENU     #############################################

        # MENU BAR
        self.menuBar = QtGui.QMenuBar(self.MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 676, 19))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))

        # MENU
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))

        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))

        self.menuSettings = QtGui.QMenu(self.menuBar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))

        # Action
        self.actionOpen = QtGui.QAction(self.MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))

        self.actionSave = QtGui.QAction(self.MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))

        self.actionAbout_ModelOrderReduction = QtGui.QAction(self.MainWindow)
        self.actionAbout_ModelOrderReduction.setObjectName(_fromUtf8("actionAbout_ModelOrderReduction"))

        self.actionSave_as = QtGui.QAction(self.MainWindow)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))

        self.actionReset = QtGui.QAction(self.MainWindow)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))

        self.actionnbr_CPU = QtGui.QAction(self.MainWindow)
        self.actionnbr_CPU.setObjectName(_fromUtf8("actionnbr_CPU"))

        self.actionverbose = QtGui.QAction(self.MainWindow)
        self.actionverbose.setObjectName(_fromUtf8("actionverbose"))

        self.actionPreferences = QtGui.QAction(self.MainWindow)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))

        # ADD Action
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addAction(self.actionReset)

        self.menuHelp.addAction(self.actionAbout_ModelOrderReduction)

        self.menuSettings.addAction(self.actionPreferences)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuSettings.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        # ADD MENU BAR
        self.MainWindow.setMenuBar(self.menuBar)

        ##########################      OTHER     ############################################

        self.MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(self.MainWindow)
        self.setPlaceHolder()

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

        self.setMaximumSize(800,600+65)
        self.setMinimumSize(600, 320) #290)

    def groupBoxScene(self,fontTitle,fontLabel,fontLineEdit,fontButton):

        # Container
        self.grpBox_Path = QtGui.QGroupBox(self.layout_path)
        self.grpBox_Path.setFont(fontTitle)
        self.grpBox_Path.setObjectName(_fromUtf8("grpBox_Path"))
        self.grpBox_Path.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        # Layout
        self.gridLayout_Path = QtGui.QGridLayout(self.grpBox_Path)
        self.gridLayout_Path.setObjectName(_fromUtf8("gridLayout_Path"))

        ########    CONTENTS    ########

        # Button
        buttonWidth = 30

        self.btn_output = QtGui.QPushButton(self.grpBox_Path)
        self.btn_output.setFixedWidth(buttonWidth)
        self.btn_output.setFont(fontButton)
        self.btn_output.setObjectName(_fromUtf8("btn_output"))

        self.btn_scene = QtGui.QPushButton(self.grpBox_Path)
        self.btn_scene.setFixedWidth(buttonWidth)
        self.btn_scene.setFont(fontButton)
        self.btn_scene.setObjectName(_fromUtf8("btn_scene"))

        self.btn_mesh = QtGui.QPushButton(self.grpBox_Path)
        self.btn_mesh.setFixedWidth(buttonWidth)
        self.btn_mesh.setFont(fontButton)
        self.btn_mesh.setObjectName(_fromUtf8("btn_mesh"))

        # LineEdit
        readOnly = True

        self.lineEdit_mesh = QtGui.QTextEdit(self.grpBox_Path)
        self.lineEdit_mesh.setFont(fontLineEdit)
        self.lineEdit_mesh.setReadOnly(readOnly)
        self.lineEdit_mesh.setObjectName(_fromUtf8("lineEdit_mesh"))

        self.lineEdit_output = QtGui.QLineEdit(self.grpBox_Path)
        self.lineEdit_output.setFont(fontLineEdit)
        self.lineEdit_output.setReadOnly(readOnly)
        self.lineEdit_output.setObjectName(_fromUtf8("lineEdit_output"))

        self.lineEdit_scene = QtGui.QLineEdit(self.grpBox_Path)
        self.lineEdit_scene.setFont(fontLineEdit)
        self.lineEdit_scene.setText(_fromUtf8(""))
        self.lineEdit_scene.setReadOnly(readOnly)
        self.lineEdit_scene.setObjectName(_fromUtf8("lineEdit_scene"))


        # Label
        self.label_mesh = QtGui.QLabel(self.grpBox_Path)
        self.label_mesh.setFont(fontLabel)
        self.label_mesh.setObjectName(_fromUtf8("label_mesh"))

        self.label_output = QtGui.QLabel(self.grpBox_Path)
        self.label_output.setFont(fontLabel)
        self.label_output.setObjectName(_fromUtf8("label_output"))

        self.label_scene = QtGui.QLabel(self.grpBox_Path)
        self.label_scene.setFont(fontLabel)
        self.label_scene.setObjectName(_fromUtf8("label_scene"))


        ################################

        # Add Contents to Layout
        self.gridLayout_Path.addWidget(self.label_scene, 0, 0, 1, 1)
        self.gridLayout_Path.addWidget(self.lineEdit_scene, 0, 1, 1, 1)
        self.gridLayout_Path.addWidget(self.btn_scene, 0, 2, 1, 1)

        self.gridLayout_Path.addWidget(self.label_mesh, 1, 0, 1, 1)
        self.gridLayout_Path.addWidget(self.lineEdit_mesh, 1, 1, 1, 1)
        self.gridLayout_Path.addWidget(self.btn_mesh, 1, 2, 1, 1)

        self.gridLayout_Path.addWidget(self.label_output, 2, 0, 1, 1)
        self.gridLayout_Path.addWidget(self.lineEdit_output, 2, 1, 1, 1)
        self.gridLayout_Path.addWidget(self.btn_output, 2, 2, 1, 1)

    def groupBoxReductionParam(self,fontTitle,fontLabel,fontLineEdit,fontCheckBox):

        # Container
        self.grpBox_ReductionParam = QtGui.QGroupBox(self.layout_reductionParam)
        self.grpBox_ReductionParam.setEnabled(True)
        self.grpBox_ReductionParam.setFont(fontTitle)
        self.grpBox_ReductionParam.setObjectName(_fromUtf8("grpBox_ReductionParam"))

        # Layout
        self.formLayout_ReductionParam = QtGui.QFormLayout(self.grpBox_ReductionParam)
        self.formLayout_ReductionParam.setObjectName(_fromUtf8("formLayout_ReductionParam"))

        ########    CONTENTS    ########

        # CheckBox

        self.checkBox_AddTranslation = QtGui.QCheckBox(self.grpBox_ReductionParam)
        self.checkBox_AddTranslation.setFont(fontCheckBox)
        self.checkBox_AddTranslation.setText(_fromUtf8(""))
        self.checkBox_AddTranslation.setObjectName(_fromUtf8("checkBox_AddTranslation"))

        # LineEdit

        self.lineEdit_moduleName = QtGui.QLineEdit(self.grpBox_ReductionParam)
        self.lineEdit_moduleName.setFont(fontLineEdit)
        self.lineEdit_moduleName.setText(_fromUtf8(""))
        self.lineEdit_moduleName.setPlaceholderText(_fromUtf8(""))
        self.lineEdit_moduleName.setObjectName(_fromUtf8("lineEdit_moduleName"))

        self.lineEdit_NodeToReduce = MyLineEdit(self.grpBox_ReductionParam)
        self.lineEdit_NodeToReduce.setFont(fontLineEdit)
        self.lineEdit_NodeToReduce.setObjectName(_fromUtf8("lineEdit_NodeToReduce"))

        # Label

        self.label_moduleName = QtGui.QLabel(self.grpBox_ReductionParam)
        self.label_moduleName.setFont(fontLabel)
        self.label_moduleName.setObjectName(_fromUtf8("label_moduleName"))

        self.label_NodeToReduce = QtGui.QLabel(self.grpBox_ReductionParam)
        self.label_NodeToReduce.setFont(fontLabel)
        self.label_NodeToReduce.setObjectName(_fromUtf8("label_NodeToReduce"))

        self.label_AddTranslation = QtGui.QLabel(self.grpBox_ReductionParam)
        self.label_AddTranslation.setFont(fontLabel)
        self.label_AddTranslation.setObjectName(_fromUtf8("label_AddTranslation"))

        ################################

        # Add Contents to Layout
        self.formLayout_ReductionParam.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_moduleName)
        self.formLayout_ReductionParam.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEdit_moduleName)

        self.formLayout_ReductionParam.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_NodeToReduce)
        self.formLayout_ReductionParam.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_NodeToReduce)

        self.formLayout_ReductionParam.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_AddTranslation)
        self.formLayout_ReductionParam.setWidget(2, QtGui.QFormLayout.FieldRole, self.checkBox_AddTranslation)

    def groupBoxAdvancedParam(self,fontTitle,fontLabel,fontLineEdit,fontCheckBox):

        # Container
        self.grpBox_AdvancedParam = QtGui.QGroupBox(self.layout_advancedParam)
        self.grpBox_AdvancedParam.setEnabled(True)
        self.grpBox_AdvancedParam.setFont(fontTitle)
        self.grpBox_AdvancedParam.setObjectName(_fromUtf8("grpBox_AdvancedParam"))

        # Layout

        self.formLayout_AdvancedParam = QtGui.QFormLayout(self.grpBox_AdvancedParam)
        self.formLayout_AdvancedParam.setObjectName(_fromUtf8("formLayout_AdvancedParam"))

        ########    CONTENTS    ########

        # CheckBox

        self.checkBox_addToLib = QtGui.QCheckBox(self.grpBox_AdvancedParam)
        self.checkBox_addToLib.setFont(fontCheckBox)
        self.checkBox_addToLib.setText(_fromUtf8(""))
        self.checkBox_addToLib.setObjectName(_fromUtf8("checkBox_addToLib"))

        # LineEdit

        self.lineEdit_toKeep = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_toKeep.setFont(fontLineEdit)
        self.lineEdit_toKeep.setObjectName(_fromUtf8("lineEdit_toKeep"))

        self.lineEdit_tolModes = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_tolModes.setFont(fontLineEdit)
        self.lineEdit_tolModes.setText(_fromUtf8(""))
        self.lineEdit_tolModes.setObjectName(_fromUtf8("lineEdit_tolModes"))

        self.lineEdit_tolGIE = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_tolGIE.setFont(fontLineEdit)
        self.lineEdit_tolGIE.setText(_fromUtf8(""))
        self.lineEdit_tolGIE.setObjectName(_fromUtf8("lineEdit_tolGIE"))

        # Label

        self.label_addToLib = QtGui.QLabel(self.grpBox_AdvancedParam)
        self.label_addToLib.setFont(fontLabel)
        self.label_addToLib.setObjectName(_fromUtf8("label_addToLib"))

        self.label_toKeep = QtGui.QLabel(self.grpBox_AdvancedParam)
        self.label_toKeep.setFont(fontLabel)
        self.label_toKeep.setObjectName(_fromUtf8("label_toKeep"))

        self.label_tolModes = QtGui.QLabel(self.grpBox_AdvancedParam)
        self.label_tolModes.setFont(fontLabel)
        self.label_tolModes.setObjectName(_fromUtf8("label_tolModes"))

        self.label_tolGIE = QtGui.QLabel(self.grpBox_AdvancedParam)
        self.label_tolGIE.setFont(fontLabel)
        self.label_tolGIE.setObjectName(_fromUtf8("label_tolGIE"))

        ################################

        # Add Contents to Layout
        self.formLayout_AdvancedParam.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_addToLib)
        self.formLayout_AdvancedParam.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_toKeep)
        self.formLayout_AdvancedParam.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_tolModes)
        self.formLayout_AdvancedParam.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_tolGIE)

        self.formLayout_AdvancedParam.setWidget(0, QtGui.QFormLayout.FieldRole, self.checkBox_addToLib)
        self.formLayout_AdvancedParam.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_toKeep)
        self.formLayout_AdvancedParam.setWidget(2, QtGui.QFormLayout.FieldRole, self.lineEdit_tolModes)
        self.formLayout_AdvancedParam.setWidget(3, QtGui.QFormLayout.FieldRole, self.lineEdit_tolGIE)

    def grouprBoxAnimationParam(self,fontTitle,fontTable,fontButton):

        # Container
        self.grpBox_AnimationParam = QtGui.QGroupBox(self.layout_aniamationParam)
        self.grpBox_AnimationParam.setEnabled(True)
        self.grpBox_AnimationParam.setFont(fontTitle)
        self.grpBox_AnimationParam.setObjectName(_fromUtf8("grpBox_AnimationParam"))

        # Layout

        self.verticalLayout_1 = QtGui.QVBoxLayout(self.grpBox_AnimationParam)
        self.verticalLayout_1.setObjectName(_fromUtf8("verticalLayout_1"))

        self.layout_addRemoveRow = QtGui.QGridLayout()
        self.layout_addRemoveRow.setObjectName(_fromUtf8("layout_addRemoveRow"))

        ########    CONTENTS    ########

        # Table

        self.tableWidget_animationParam = QtGui.QTableWidget(self.grpBox_AnimationParam)
        self.tableWidget_animationParam.setFont(fontTable)
        self.tableWidget_animationParam.setObjectName(_fromUtf8("tableWidget_animationParam"))
        self.tableWidget_animationParam.setColumnCount(3)
        self.tableWidget_animationParam.setRowCount(0)

        item = QtGui.QTableWidgetItem()
        item.setText(_translate("MainWindow", "parameters", None))
        self.tableWidget_animationParam.setHorizontalHeaderItem(0, item)
        self.tableWidget_animationParam.setColumnWidth(1, 80)

        item = QtGui.QTableWidgetItem()
        item.setText(_translate("MainWindow", "animation function", None))
        self.tableWidget_animationParam.setHorizontalHeaderItem(1, item)
        self.tableWidget_animationParam.setColumnWidth(2, 90)

        item = QtGui.QTableWidgetItem()
        item.setText(_translate("MainWindow", "to Animate", None))
        self.tableWidget_animationParam.setHorizontalHeaderItem(2, item)
        self.tableWidget_animationParam.setColumnWidth(0, 90)

        self.tableWidget_animationParam.verticalHeader().hide()

        # Button

        self.btn_addLine = QtGui.QPushButton(self.grpBox_AnimationParam)
        self.btn_addLine.setFont(fontButton)
        self.btn_addLine.setObjectName(_fromUtf8("btn_addLine"))

        self.btn_removeLine = QtGui.QPushButton(self.grpBox_AnimationParam)
        self.btn_removeLine.setFont(fontButton)
        self.btn_removeLine.setObjectName(_fromUtf8("btn_removeLine"))

        # Spacer

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        ################################

        # Add Contents to Layout
        self.layout_addRemoveRow.addWidget(self.btn_removeLine, 1, 2, 1, 1)
        self.layout_addRemoveRow.addWidget(self.btn_addLine, 1, 1, 1, 1)
        self.layout_addRemoveRow.addItem(spacerItem, 1, 0, 1, 1)

        self.verticalLayout_1.addWidget(self.tableWidget_animationParam)
        self.verticalLayout_1.addLayout(self.layout_addRemoveRow)

    def groupBoxExecution(self,fontTitle,fontLineEdit):

        # Container
        self.grpBox_Execution = QtGui.QGroupBox(self.layout_execution)
        self.grpBox_Execution.setEnabled(True)
        self.grpBox_Execution.setFont(fontTitle)
        self.grpBox_Execution.setObjectName(_fromUtf8("grpBox_Execution"))

        # Layout
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpBox_Execution)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))

        ########    CONTENTS    ########

        # Frame Layout

        self.phase1 = FrameLayout(self.grpBox_Execution,title="Phase 1")
        self.phase1.setObjectName('Phase 1')

        self.phase2 = FrameLayout(self.grpBox_Execution,title="Phase 2")
        self.phase2.setObjectName('Phase 2')

        self.phase3 = FrameLayout(self.grpBox_Execution,title="Phase 3")
        self.phase3.setObjectName('Phase 3')

        self.phase4 = FrameLayout(self.grpBox_Execution,title="Phase 4")
        self.phase4.setObjectName('Phase 4')

        # TextBrowser

        textBrowser = QtGui.QTextBrowser(self.phase1)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText("Phase 1 Description")
        self.phase1.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        textBrowser = QtGui.QTextBrowser(self.phase2)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText("Phase 2 Description")
        self.phase2.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        textBrowser = QtGui.QTextBrowser(self.phase3)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText("Phase 3 Description")
        self.phase3.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        textBrowser = QtGui.QTextBrowser(self.phase4)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText("Phase 4 Description")
        self.phase4.addWidget(textBrowser)

        ################################

        # Add Contents to Layout
        self.verticalLayout_2.addWidget(self.phase1)
        self.verticalLayout_2.addWidget(self.phase2)
        self.verticalLayout_2.addWidget(self.phase3)
        self.verticalLayout_2.addWidget(self.phase4)

    def retranslateUi(self, MainWindow):

        MainWindow.setWindowTitle(_translate("Model Order Reduction Plugin", "Model Order Reduction Plugin", None))

        ##########################      GROUPBOX PATH     ####################################

        self.grpBox_Path.setTitle(_translate("MainWindow", "", None))

        self.label_scene.setText(_translate("MainWindow", "Scene", None))
        self.label_mesh.setText(_translate("MainWindow", "mesh", None))
        self.label_output.setText(_translate("MainWindow", "Output", None))

        self.btn_scene.setText(_translate("MainWindow", "...", None))
        self.btn_mesh.setText(_translate("MainWindow", "...", None))
        self.btn_output.setText(_translate("MainWindow", "...", None))

        ##########################      GROUPBOX REDUCTION PARAM     #########################

        self.grpBox_ReductionParam.setTitle(_translate("MainWindow", "", None))

        self.label_moduleName.setText(_translate("MainWindow", "Module Name", None))
        self.label_NodeToReduce.setText(_translate("MainWindow", "Node To Reduce", None))
        self.label_AddTranslation.setText(_translate("MainWindow", "Add Translation", None))

        ##########################      GROUPBOX ADVANCED PARAM     ##########################

        self.grpBox_AdvancedParam.setTitle(_translate("MainWindow", "", None))

        self.label_addToLib.setText(_translate("MainWindow", "Add to lib", None))
        self.label_tolModes.setText(_translate("MainWindow", "Tolerance Modes", None))
        self.label_toKeep.setText(_translate("MainWindow", "To keep", None))
        self.label_tolGIE.setText(_translate("MainWindow", "Tolerance GIE", None))

        ##########################      GROUPBOX ANIAMATION PARAM     ########################

        self.tableWidget_animationParam.horizontalHeader().setStretchLastSection(True)

        self.btn_addLine.setText(_translate("MainWindow", "Add", None))
        self.btn_removeLine.setText(_translate("MainWindow", "Remove", None))

        self.tableWidget_animationParam.resizeColumnsToContents()

        ##########################      GROUPBOX EXECUTION     ###############################


        ##########################      LAUNCH REDUCTION     #################################

        self.btn_launchReduction.setText(_translate("MainWindow", "Launch Reduction", None))

        ##########################      MENU     #############################################

        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings", None))

        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S", None))
        self.actionAbout_ModelOrderReduction.setText(_translate("MainWindow", "About ModelOrderReduction", None))
        self.actionSave_as.setText(_translate("MainWindow", "Save as...", None))
        self.actionReset.setText(_translate("MainWindow", "Reset", None))
        self.actionReset.setShortcut(_translate("MainWindow", "Ctrl+R", None))
        self.actionnbr_CPU.setText(_translate("MainWindow", "nbr CPU", None))
        self.actionverbose.setText(_translate("MainWindow", "verbose", None))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences...", None))

    def setPlaceHolder(self):

        ##########################      GROUPBOX PATH     ####################################
        self.lineEdit_output.setPlaceholderText(_translate("MainWindow", "Choose in which folder all the outputs will be placed", None))
        self.lineEdit_scene.setPlaceholderText(_translate("MainWindow", "Choose your sofa scene you want to reduce (.scn/.py/.pyscn)", None))

        # self.lineEdit_mesh.setPlaceholderText(_translate("MainWindow", "select all the meshes that your Sofa scene need, they will be copied and put in a mesh folder in the output folder", None))

        ##########################      GROUPBOX REDUCTION PARAM     #########################
        self.lineEdit_NodeToReduce.setPlaceholderText(_translate("MainWindow", "/path/ofMy/sofaNode/inMyScene", None))

        self.label_NodeToReduce.setToolTip(_translate("MainWindow", "paths to models to reduce", None))
        self.label_AddTranslation.setToolTip(_translate("MainWindow", "allow translation along [x,y,z] axis of our reduced model", None))
        self.label_tolModes.setToolTip(_translate("MainWindow", "tolerance applied to choose the modes", None))
        self.label_tolGIE.setToolTip(_translate("MainWindow", "tolerance applied to calculated GIE", None))

        ##########################      GROUPBOX ADVANCED PARAM     ##########################


        ##########################      GROUPBOX ANIAMATION PARAM     ########################


        ##########################      GROUPBOX EXECUTION     ###############################


        ##########################      LAUNCH REDUCTION     #################################