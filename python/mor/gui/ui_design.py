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
'''
**Module describing the visual of MOR GUI**
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import QObject

import os
import sys
from collections import OrderedDict

# MOR IMPORT
path = os.path.dirname(os.path.abspath(__file__))
pathToIcon = path+'/icons/'

from mor.gui.widget import FrameLayout
from mor.gui.widget import GenericDialogForm
from mor.gui.widget import LineEdit
from mor.gui.widget import AnimationTableWidget

from mor.gui.widget import widgetUtility

from mor.gui.settings.ui_colors import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)



class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        # MAIN WINDOW
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.MainWindow.setMinimumSize(600, 320) #290)
        self.MainWindow.setMaximumSize(800, 600+65)
        self.MainWindow.layout().setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        # self.MainWindow.setStyleSheet("margin: 0px; border: 2px solid green;") # padding: 20px;") # background-color:grey;

        # CENTRAL WIDGET
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        # SCROLL AREA
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))

        self.scrollArea.setStyleSheet('QWidget#scrollArea {border: 0px;} QToolTip{background-color: white;color: black;border: black solid 2px} ')
        # self.scrollArea.setStyleSheet("border: 0px;") # padding: 20px;") # background-color:grey;
        self.scrollArea.setWidget(QtWidgets.QWidget(self.centralwidget))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMaximumSize(800,600)

        # MAIN LAYOUTS

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        # self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop)

        self.scrollArea_layout = QtWidgets.QVBoxLayout(self.scrollArea.widget())
        self.scrollArea_layout.setContentsMargins(0,0,0,0) # setMargin(0)
        self.scrollArea_layout.setSpacing(0)
        self.scrollArea_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize) #QLayout.SetFixedSize)

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

        self.groupBoxAdvancedParam(fontTitle,fontLabel,fontLineEdit,fontCheckBox,fontButton)

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

        self.groupBoxExecution(fontTitle,fontLineEdit,fontButton)

        self.layout_execution.addWidget(self.grpBox_Execution)
        self.scrollArea_layout.addWidget(self.layout_execution) #, 0, QtCore.Qt.AlignTop)


        ##########################      LAUNCH REDUCTION     #################################

        # Layout
        self.layout_launchReduction = QtWidgets.QGridLayout()
        self.layout_launchReduction.setObjectName(_fromUtf8("layout_launchReduction"))

        ########    CONTENTS    ########

        # Separator Line
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName(_fromUtf8("line"))

        # Button
        self.btn_launchReduction = QtWidgets.QPushButton(self.centralwidget)
        self.btn_launchReduction.setObjectName(_fromUtf8("btn_launchReduction"))


        # Spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        ################################

        # Add Contents to Layout
        self.layout_launchReduction.addWidget(self.btn_launchReduction, 1, 1, 1, 1)
        self.layout_launchReduction.addItem(spacerItem, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.line)
        self.verticalLayout.addLayout(self.layout_launchReduction)

        ##########################      MENU     #############################################

        # MENU BAR
        self.menuBar = QtWidgets.QMenuBar(self.MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 676, 19))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))

        # MENU
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))

        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))

        self.menuSettings = QtWidgets.QMenu(self.menuBar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))

        # Action
        self.actionOpen = QtWidgets.QAction(self.MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))

        self.actionSave = QtWidgets.QAction(self.MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))

        self.actionWebsite = QtWidgets.QAction(self.MainWindow)
        self.actionWebsite.setObjectName(_fromUtf8("actionWebsite"))

        self.actionGithub = QtWidgets.QAction(self.MainWindow)
        self.actionGithub.setObjectName(_fromUtf8("actionGithub"))

        self.actionDoc = QtWidgets.QAction(self.MainWindow)
        self.actionDoc.setObjectName(_fromUtf8("actionDoc"))

        self.actionSave_as = QtWidgets.QAction(self.MainWindow)
        self.actionSave_as.setObjectName(_fromUtf8("actionSave_as"))

        self.actionReset = QtWidgets.QAction(self.MainWindow)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))

        self.actionnbr_CPU = QtWidgets.QAction(self.MainWindow)
        self.actionnbr_CPU.setObjectName(_fromUtf8("actionnbr_CPU"))

        self.actionverbose = QtWidgets.QAction(self.MainWindow)
        self.actionverbose.setObjectName(_fromUtf8("actionverbose"))

        self.actionPreferences = QtWidgets.QAction(self.MainWindow)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))

        # ADD Action
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addAction(self.actionReset)

        self.menuHelp.addAction(self.actionDoc)
        self.menuHelp.addAction(self.actionWebsite)
        self.menuHelp.addAction(self.actionGithub)


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

        # Set the different grpBoxes of our application
        # It will ease the way we iterate on them
        self.grpBoxes = [ self.grpBox_Path,
                          self.grpBox_AdvancedParam,
                          self.grpBox_ReductionParam,
                          self.grpBox_AnimationParam,
                          self.grpBox_Execution]

        # Main layout of app
        self.listLayout = [self.layout_path,self.layout_aniamationParam,self.layout_reductionParam,
                           self.layout_advancedParam,self.layout_execution]

        # to ease access
        self.phases = [self.phase1,self.phase2,self.phase3,self.phase4]
        self.phaseItem = []
        for phase in self.phases:
            self.phaseItem.append(widgetUtility.addButton(phase,self.grpBox_Execution))


        self.mandatoryFields = OrderedDict([
            (self.lineEdit_scene,                self.label_scene),
            (self.lineEdit_output,               self.label_output),
            (self.lineEdit_NodeToReduce,         self.label_NodeToReduce),
            (self.tab_animation,                 self.layout_aniamationParam),
            (self.lineEdit_tolGIE,               self.label_tolGIE),
            (self.lineEdit_tolModes,             self.label_tolModes)
            # (self.lineEdit_phasesToExecute,      self.label_phasesToExecute)
        ])

    def groupBoxScene(self,fontTitle,fontLabel,fontLineEdit,fontButton):

        # Container
        self.grpBox_Path = QtWidgets.QGroupBox(self.layout_path)
        self.grpBox_Path.setFont(fontTitle)
        self.grpBox_Path.setObjectName(_fromUtf8("grpBox_Path"))
        self.grpBox_Path.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        # Layout
        self.gridLayout_Path = QtWidgets.QGridLayout(self.grpBox_Path)
        self.gridLayout_Path.setObjectName(_fromUtf8("gridLayout_Path"))

        ########    CONTENTS    ########

        # Button
        buttonWidth = 30

        self.btn_output = QtWidgets.QPushButton(self.grpBox_Path)
        self.btn_output.setFixedWidth(buttonWidth)
        self.btn_output.setFont(fontButton)
        self.btn_output.setObjectName(_fromUtf8("btn_output"))

        self.btn_scene = QtWidgets.QPushButton(self.grpBox_Path)
        self.btn_scene.setFixedWidth(buttonWidth)
        self.btn_scene.setFont(fontButton)
        self.btn_scene.setObjectName(_fromUtf8("btn_scene"))

        # LineEdit
        readOnly = True

        self.lineEdit_output = QtWidgets.QLineEdit(self.grpBox_Path)
        self.lineEdit_output.setFont(fontLineEdit)
        self.lineEdit_output.setReadOnly(readOnly)
        self.lineEdit_output.setObjectName(_fromUtf8("lineEdit_output"))

        self.lineEdit_scene = QtWidgets.QLineEdit(self.grpBox_Path)
        self.lineEdit_scene.setFont(fontLineEdit)
        self.lineEdit_scene.setText(_fromUtf8(""))
        self.lineEdit_scene.setReadOnly(readOnly)
        self.lineEdit_scene.setObjectName(_fromUtf8("lineEdit_scene"))


        # Label
        self.label_output = QtWidgets.QLabel(self.grpBox_Path)
        self.label_output.setFont(fontLabel)
        self.label_output.setObjectName(_fromUtf8("label_output"))

        self.label_scene = QtWidgets.QLabel(self.grpBox_Path)
        self.label_scene.setFont(fontLabel)
        self.label_scene.setObjectName(_fromUtf8("label_scene"))


        ################################

        # Add Contents to Layout
        self.gridLayout_Path.addWidget(self.label_scene, 0, 0, 1, 1)
        self.gridLayout_Path.addWidget(self.lineEdit_scene, 0, 1, 1, 1)
        self.gridLayout_Path.addWidget(self.btn_scene, 0, 2, 1, 1)

        self.gridLayout_Path.addWidget(self.label_output, 2, 0, 1, 1)
        self.gridLayout_Path.addWidget(self.lineEdit_output, 2, 1, 1, 1)
        self.gridLayout_Path.addWidget(self.btn_output, 2, 2, 1, 1)

    def groupBoxReductionParam(self,fontTitle,fontLabel,fontLineEdit,fontCheckBox):

        # Container
        self.grpBox_ReductionParam = QtWidgets.QGroupBox(self.layout_reductionParam)
        self.grpBox_ReductionParam.setEnabled(True)
        self.grpBox_ReductionParam.setFont(fontTitle)
        self.grpBox_ReductionParam.setObjectName(_fromUtf8("grpBox_ReductionParam"))

        # Layout
        self.formLayout_ReductionParam = QtWidgets.QFormLayout(self.grpBox_ReductionParam)
        self.formLayout_ReductionParam.setObjectName(_fromUtf8("formLayout_ReductionParam"))

        ########    CONTENTS    ########

        # CheckBox

        self.checkBox_AddTranslation = QtWidgets.QCheckBox(self.grpBox_ReductionParam)
        self.checkBox_AddTranslation.setFont(fontCheckBox)
        self.checkBox_AddTranslation.setText(_fromUtf8(""))
        self.checkBox_AddTranslation.setObjectName(_fromUtf8("checkBox_AddTranslation"))

        # LineEdit

        self.lineEdit_moduleName = QtWidgets.QLineEdit(self.grpBox_ReductionParam)
        self.lineEdit_moduleName.setFont(fontLineEdit)
        self.lineEdit_moduleName.setText(_fromUtf8(""))
        self.lineEdit_moduleName.setPlaceholderText(_fromUtf8(""))
        self.lineEdit_moduleName.setObjectName(_fromUtf8("lineEdit_moduleName"))

        self.lineEdit_NodeToReduce = LineEdit(self.grpBox_ReductionParam)
        self.lineEdit_NodeToReduce.setFont(fontLineEdit)
        self.lineEdit_NodeToReduce.setObjectName(_fromUtf8("lineEdit_NodeToReduce"))
        self.lineEdit_NodeToReduce.setReadOnly(True)

        # Label

        self.label_moduleName = QtWidgets.QLabel(self.grpBox_ReductionParam)
        self.label_moduleName.setFont(fontLabel)
        self.label_moduleName.setObjectName(_fromUtf8("label_moduleName"))

        self.label_NodeToReduce = QtWidgets.QLabel(self.grpBox_ReductionParam)
        self.label_NodeToReduce.setFont(fontLabel)
        self.label_NodeToReduce.setObjectName(_fromUtf8("label_NodeToReduce"))

        self.label_AddTranslation = QtWidgets.QLabel(self.grpBox_ReductionParam)
        self.label_AddTranslation.setFont(fontLabel)
        self.label_AddTranslation.setObjectName(_fromUtf8("label_AddTranslation"))

        ################################

        # Add Contents to Layout
        self.formLayout_ReductionParam.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_moduleName)
        self.formLayout_ReductionParam.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_moduleName)

        self.formLayout_ReductionParam.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_NodeToReduce)
        self.formLayout_ReductionParam.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_NodeToReduce)

        self.formLayout_ReductionParam.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_AddTranslation)
        self.formLayout_ReductionParam.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.checkBox_AddTranslation)

    def groupBoxAdvancedParam(self,fontTitle,fontLabel,fontLineEdit,fontCheckBox,fontButton):

        # Container
        self.grpBox_AdvancedParam = QtWidgets.QGroupBox(self.layout_advancedParam)
        self.grpBox_AdvancedParam.setEnabled(True)
        self.grpBox_AdvancedParam.setFont(fontTitle)
        self.grpBox_AdvancedParam.setObjectName(_fromUtf8("grpBox_AdvancedParam"))

        # Layout

        self.vLayout_advancedParam = QtWidgets.QVBoxLayout(self.grpBox_AdvancedParam)
        self.vLayout_advancedParam.setObjectName(_fromUtf8("verticalLayout_advancedParam"))

        self.formLayout_AdvancedParam = QtWidgets.QFormLayout()
        self.formLayout_AdvancedParam.setObjectName(_fromUtf8("formLayout_AdvancedParam"))

        self.gridLayout_Phase = QtWidgets.QGridLayout()
        self.gridLayout_Phase.setObjectName(_fromUtf8("gridLayout_Path"))

        ########    CONTENTS    ########

        # CheckBox

        self.checkBox_addToLib = QtWidgets.QCheckBox(self.grpBox_AdvancedParam)
        self.checkBox_addToLib.setFont(fontCheckBox)
        self.checkBox_addToLib.setText(_fromUtf8(""))
        self.checkBox_addToLib.setObjectName(_fromUtf8("checkBox_addToLib"))

        self.checkBox_auto = QtWidgets.QCheckBox(self.grpBox_AdvancedParam)
        self.checkBox_auto.setFont(fontCheckBox)
        self.checkBox_auto.setText(_fromUtf8(""))
        self.checkBox_auto.setObjectName(_fromUtf8("checkBox_auto"))
        self.checkBox_auto.setCheckState(True)
        self.checkBox_auto.setTristate(False)

        # Button
        buttonWidth = 30

        self.btn_animationPath = QtWidgets.QPushButton(self.grpBox_AdvancedParam)
        self.btn_animationPath.setFixedWidth(buttonWidth)
        self.btn_animationPath.setFont(fontButton)
        self.btn_animationPath.setObjectName(_fromUtf8("btn_animationPath"))

        # LineEdit
        readOnly = True

        self.lineEdit_tolModes = QtWidgets.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_tolModes.setFont(fontLineEdit)
        self.lineEdit_tolModes.setText(_fromUtf8(""))
        self.lineEdit_tolModes.setObjectName(_fromUtf8("lineEdit_tolModes"))

        self.lineEdit_tolGIE = QtWidgets.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_tolGIE.setFont(fontLineEdit)
        self.lineEdit_tolGIE.setText(_fromUtf8(""))
        self.lineEdit_tolGIE.setObjectName(_fromUtf8("lineEdit_tolGIE"))

        self.lineEdit_phasesToExecute = QtWidgets.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_phasesToExecute.setFont(fontLineEdit)
        self.lineEdit_phasesToExecute.setText(_fromUtf8(""))
        self.lineEdit_phasesToExecute.setObjectName(_fromUtf8("lineEdit_phasesToExecute"))
        self.lineEdit_phasesToExecute.setDisabled(True)

        self.lineEdit_animationPath = QtWidgets.QLineEdit(self.grpBox_AdvancedParam)
        self.lineEdit_animationPath.setFont(fontLineEdit)
        self.lineEdit_animationPath.setText(_fromUtf8(""))
        self.lineEdit_animationPath.setReadOnly(readOnly)
        self.lineEdit_animationPath.setObjectName(_fromUtf8("lineEdit_animationPath"))

        # Label

        self.label_addToLib = QtWidgets.QLabel(self.grpBox_AdvancedParam)
        self.label_addToLib.setFont(fontLabel)
        self.label_addToLib.setObjectName(_fromUtf8("label_addToLib"))

        self.label_tolModes = QtWidgets.QLabel(self.grpBox_AdvancedParam)
        self.label_tolModes.setFont(fontLabel)
        self.label_tolModes.setObjectName(_fromUtf8("label_tolModes"))

        self.label_tolGIE = QtWidgets.QLabel(self.grpBox_AdvancedParam)
        self.label_tolGIE.setFont(fontLabel)
        self.label_tolGIE.setObjectName(_fromUtf8("label_tolGIE"))

        self.label_phasesToExecute = QtWidgets.QLabel(self.grpBox_AdvancedParam)
        self.label_phasesToExecute.setFont(fontLabel)
        self.label_phasesToExecute.setObjectName(_fromUtf8("label_phasesToExecute"))

        self.label_animationPath = QtWidgets.QLabel(self.grpBox_AdvancedParam)
        self.label_animationPath.setFont(fontLabel)
        self.label_animationPath.setObjectName(_fromUtf8("label_animationPath"))
        ################################

        # Add Contents to Layout
        self.formLayout_AdvancedParam.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_addToLib)
        self.formLayout_AdvancedParam.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_tolModes)
        self.formLayout_AdvancedParam.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_tolGIE)
        # self.formLayout_AdvancedParam.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_phasesToExecute)

        self.formLayout_AdvancedParam.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.checkBox_addToLib)
        self.formLayout_AdvancedParam.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_tolModes)
        self.formLayout_AdvancedParam.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_tolGIE)
        # self.formLayout_AdvancedParam.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_phasesToExecute)

        self.gridLayout_Phase.addWidget(self.label_phasesToExecute, 0, 0, 1, 1)
        self.gridLayout_Phase.addWidget(self.lineEdit_phasesToExecute, 0, 1, 1, 1)
        self.gridLayout_Phase.addWidget(self.checkBox_auto, 0, 2, 1, 1)

        self.gridLayout_Phase.addWidget(self.label_animationPath, 2, 0, 1, 1)
        self.gridLayout_Phase.addWidget(self.lineEdit_animationPath, 2, 1, 1, 1)
        self.gridLayout_Phase.addWidget(self.btn_animationPath, 2, 2, 1, 1)

        self.vLayout_advancedParam.addLayout(self.formLayout_AdvancedParam)
        self.vLayout_advancedParam.addLayout(self.gridLayout_Phase)

    def grouprBoxAnimationParam(self,fontTitle,fontTable,fontButton):

        # Container
        self.grpBox_AnimationParam = QtWidgets.QGroupBox(self.layout_aniamationParam)
        self.grpBox_AnimationParam.setEnabled(True)
        self.grpBox_AnimationParam.setFont(fontTitle)
        self.grpBox_AnimationParam.setObjectName(_fromUtf8("grpBox_AnimationParam"))

        # Layout

        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.grpBox_AnimationParam)
        self.verticalLayout_1.setObjectName(_fromUtf8("verticalLayout_1"))

        self.layout_addRemoveRow = QtWidgets.QGridLayout()
        self.layout_addRemoveRow.setObjectName(_fromUtf8("layout_addRemoveRow"))

        ########    CONTENTS    ########

        # Table
        var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_
        self.tab_animation = AnimationTableWidget(self.grpBox_AnimationParam,QtCore.QRegExp("^("+var_semantic+"){1}(\\/"+var_semantic+")*$"))
        self.tab_animation.setFont(fontTable)
        self.tab_animation.setObjectName(_fromUtf8("tab_animation"))
        self.tab_animation.setColumnCount(4)
        self.tab_animation.setRowCount(0)

        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("MainWindow", "", None))
        self.tab_animation.setHorizontalHeaderItem(0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("MainWindow", "animation function", None))
        self.tab_animation.setHorizontalHeaderItem(1, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("MainWindow", "parameters", None))
        self.tab_animation.setHorizontalHeaderItem(2, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(_translate("MainWindow", "to Animate", None))
        self.tab_animation.setHorizontalHeaderItem(3, item)

        header = self.tab_animation.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)


        self.tab_animation.verticalHeader().hide()
        self.tab_animation.horizontalHeader().setMinimumSectionSize(16)

        # Button

        self.btn_addLine = QtWidgets.QPushButton(self.grpBox_AnimationParam)
        self.btn_addLine.setFont(fontButton)
        self.btn_addLine.setObjectName(_fromUtf8("btn_addLine"))

        self.btn_removeLine = QtWidgets.QPushButton(self.grpBox_AnimationParam)
        self.btn_removeLine.setFont(fontButton)
        self.btn_removeLine.setObjectName(_fromUtf8("btn_removeLine"))

        self.btn_test1 = QtWidgets.QPushButton(self.grpBox_AnimationParam)
        self.btn_test1.setFont(fontButton)
        self.btn_test1.setObjectName(_fromUtf8("btn_test1"))

        # Spacer

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        ################################

        # Add Contents to Layout
        self.layout_addRemoveRow.addWidget(self.btn_test1, 1, 0, 1, 1)
        self.layout_addRemoveRow.addWidget(self.btn_removeLine, 1, 3, 1, 1)
        self.layout_addRemoveRow.addWidget(self.btn_addLine, 1, 2, 1, 1)
        self.layout_addRemoveRow.addItem(spacerItem, 1, 1, 1, 1)

        self.verticalLayout_1.addWidget(self.tab_animation)
        self.verticalLayout_1.addLayout(self.layout_addRemoveRow)

    def groupBoxExecution(self,fontTitle,fontLineEdit,fontButton):

        # Phase Description

        phase1Info = (  "Snapshot Database Computation\n\n"
                        "We modify the original scene to do the first step of MOR :\n"
                        "     - We add animation to each actuators we want for our model\n"
                        "     - And add a writeState componant to save the shaking resulting states")

        phase2Info = (  "Computation of the reduced basis with SVD decomposition\n\n"
                        "With the previous result we combine all the generated state files into one to be able to extract from it the different mode")

        phase3Info = (  "Reduced Snapshot Computation to store projected FEM internal forces contributions\n\n"
                        "We launch again a set of sofa scene with the sofa launcher with the same previous arguments but with a different scene\n"
                        "This scene take the previous one and add the model order reduction component:\n"
                        "    - HyperReducedFEMForceField\n"
                        "    - ModelOrderReductionMapping and produce an Hyper Reduced description of the model")

        phase4Info = (  "Computation of the reduced integration domain in terms of elements and nodes\n\n"
                        "Final step :\n"
                        "   - We gather again all the results of the previous scenes into one and then compute the RID and Weigts with it.\n"
                        "   - Additionnally we also compute the Active Nodes\n")

        # Container
        self.grpBox_Execution = QtWidgets.QGroupBox(self.layout_execution)
        self.grpBox_Execution.setEnabled(True)
        self.grpBox_Execution.setFont(fontTitle)
        self.grpBox_Execution.setObjectName(_fromUtf8("grpBox_Execution"))

        # Layout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpBox_Execution)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))

        ########    CONTENTS    ########

        # Frame Layout

        self.phase1 = FrameLayout(self.grpBox_Execution,title="Phase 1: Snapshot Database Computation")
        self.phase1.setObjectName('Phase 1')

        # self.layout_phase1TestDebug = QtWidgets.QGridLayout(self.phase1)
        # self.layout_phase1TestDebug.setObjectName(_fromUtf8("layout_phase1TestDebug"))

        self.phase2 = FrameLayout(self.grpBox_Execution,title="Phase 2: Computation of the reduced basis")
        self.phase2.setObjectName('Phase 2')

        self.phase3 = FrameLayout(self.grpBox_Execution,title="Phase 3: Reduced Snapshot Computation")
        self.phase3.setObjectName('Phase 3')

        self.phase4 = FrameLayout(self.grpBox_Execution,title="Phase 4: Computation of the reduced integration domain")
        self.phase4.setObjectName('Phase 4')

        # TextBrowser

        textBrowser = QtWidgets.QTextBrowser(self.phase1)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText(phase1Info)
        self.phase1.addWidget(textBrowser)

        textBrowser = QtWidgets.QTextBrowser()
        textBrowser = QtWidgets.QTextBrowser(self.phase2)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText(phase2Info)
        self.phase2.addWidget(textBrowser)

        textBrowser = QtWidgets.QTextBrowser()
        textBrowser = QtWidgets.QTextBrowser(self.phase3)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText(phase3Info)
        self.phase3.addWidget(textBrowser)

        textBrowser = QtWidgets.QTextBrowser()
        textBrowser = QtWidgets.QTextBrowser(self.phase4)
        textBrowser.setFont(fontLineEdit)
        textBrowser.setText(phase4Info)
        self.phase4.addWidget(textBrowser)

        # Button

        self.btn_debug1 = QtWidgets.QPushButton(self.phase1)
        self.btn_debug1.setFont(fontButton)
        self.btn_debug1.setObjectName(_fromUtf8("btn_debug1"))
        self.phase1.addWidget(self.btn_debug1)

        # self.layout_phase1TestDebug.addWidget(self.btn_test, 0, 0, 1, 1)
        # self.layout_phase1TestDebug.addWidget(self.btn_debug1, 0, 1, 1, 1)

        self.btn_test2 = QtWidgets.QPushButton(self.phase3)
        self.btn_test2.setFont(fontButton)
        self.btn_test2.setObjectName(_fromUtf8("btn_test2"))
        self.phase3.addWidget(self.btn_test2)

        self.btn_debug2 = QtWidgets.QPushButton(self.phase3)
        self.btn_debug2.setFont(fontButton)
        self.btn_debug2.setObjectName(_fromUtf8("btn_debug2"))
        self.phase3.addWidget(self.btn_debug2)

        self.btn_results = QtWidgets.QPushButton(self.phase4)
        self.btn_results.setFont(fontButton)
        self.btn_results.setObjectName(_fromUtf8("btn_results"))
        self.phase4.addWidget(self.btn_results)

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
        self.label_output.setText(_translate("MainWindow", "Output", None))

        self.btn_scene.setText(_translate("MainWindow", "...", None))
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
        self.label_tolGIE.setText(_translate("MainWindow", "Tolerance GIE", None))
        self.label_phasesToExecute.setText(_translate("MainWindow", "Phase to execute", None))
        self.label_animationPath.setText(_translate("MainWindow", "Path to Animation", None))

        self.btn_animationPath.setText(_translate("MainWindow", "...", None))

        ##########################      GROUPBOX ANIAMATION PARAM     ########################

        self.tab_animation.horizontalHeader().setStretchLastSection(True)

        self.btn_test1.setText(_translate("MainWindow", "Test animation", None))
        self.btn_addLine.setText(_translate("MainWindow", "Add", None))
        self.btn_removeLine.setText(_translate("MainWindow", "Remove", None))

        self.tab_animation.resizeColumnsToContents()

        ##########################      GROUPBOX EXECUTION     ###############################

        self.btn_debug1.setText(_translate("MainWindow", "launch debug phase", None))
        self.btn_test2.setText(_translate("MainWindow", "Test reduction", None))
        self.btn_debug2.setText(_translate("MainWindow", "launch debug phase", None))
        self.btn_results.setText(_translate("MainWindow", "launch result", None))

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
        self.actionDoc.setText(_translate("MainWindow", "link to doc", None))
        self.actionWebsite.setText(_translate("MainWindow", "link to website", None))
        self.actionGithub.setText(_translate("MainWindow", "link to github", None))
        self.actionSave_as.setText(_translate("MainWindow", "Save as...", None))
        self.actionReset.setText(_translate("MainWindow", "Reset", None))
        self.actionReset.setShortcut(_translate("MainWindow", "Ctrl+R", None))
        self.actionnbr_CPU.setText(_translate("MainWindow", "nbr CPU", None))
        self.actionverbose.setText(_translate("MainWindow", "verbose", None))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences...", None))

    def setPlaceHolder(self):

        ##########################      GROUPBOX PATH     ####################################
        self.layout_path._title_frame.setToolTip(_translate("MainWindow", "contains all the I/O file/folder parameters", None))

        self.lineEdit_scene.setPlaceholderText(_translate("MainWindow", "Choose your sofa scene you want to reduce (.scn/.py/.pyscn)", None))
        self.lineEdit_output.setPlaceholderText(_translate("MainWindow", "Choose in which folder all the outputs will be placed", None))

        self.label_scene.setToolTip(_translate("MainWindow", "original scene (input)", None))
        self.label_output.setToolTip(_translate("MainWindow", "output folder", None))

        ##########################      GROUPBOX REDUCTION PARAM     #########################
        self.layout_reductionParam._title_frame.setToolTip(_translate("MainWindow", "contains the main parameters to reduce our model", None))


        self.label_moduleName.setToolTip(_translate("MainWindow", "name of the re-usable component created at the end of the reduction", None))
        self.label_NodeToReduce.setToolTip(_translate("MainWindow", "paths in the SOFA scene toward the models to reduce", None))
        self.label_AddTranslation.setToolTip(_translate("MainWindow", "allow translation along [x,y,z] axis of our reduced model", None))

        self.lineEdit_NodeToReduce.setPlaceholderText(_translate("MainWindow", "/path/ofMy/sofaNode/inMyScene", None))

        ##########################      GROUPBOX ADVANCED PARAM     ##########################
        self.layout_advancedParam._title_frame.setToolTip(_translate("MainWindow", "contains more advanced parameters,\nusually put to their default value", None))


        self.label_addToLib.setToolTip(_translate("MainWindow", "Add to the library ModelOrderReduction/python/morlib\nyour reduce model in order to re-use it easily in other scene", None))

        self.label_tolModes.setToolTip(_translate("MainWindow", "Defines the level of accuracy we want to select the reduced basis modes,\nhight/low tolerance wil select many/few modes", None))
        self.label_tolGIE.setToolTip(_translate("MainWindow", "tolerance used in the greedy algorithm selecting the reduced integration domain(RID).\nValues are between 0 and 0.1 .\nHigh values will lead to RIDs with very few elements, while values approaching 0 will lead to large RIDs.  Typically set to 0.05", None))
        self.label_phasesToExecute.setToolTip(_translate("MainWindow", "Actuation pattern you want to execute during the reduction", None))

        ##########################      GROUPBOX ANIAMATION PARAM     ########################
        self.layout_aniamationParam._title_frame.setToolTip(_translate("MainWindow", "contains the parameters allowing to define our model animation", None))
        self.tab_animation.horizontalHeaderItem(0).setToolTip(_translate("MainWindow", "Select with which animation fct to work", None))
        self.tab_animation.horizontalHeaderItem(1).setToolTip(_translate("MainWindow", "Parameters for the animation function", None))
        self.tab_animation.horizontalHeaderItem(2).setToolTip(_translate("MainWindow", "Path in the SOFA scene toward the SOFA.node/obj you want to aply the animation fct on", None))

        ##########################      GROUPBOX EXECUTION     ###############################
        self.layout_execution._title_frame.setToolTip(_translate("MainWindow", "contains the different execution you can perform", None))


        ##########################      LAUNCH REDUCTION     #################################
