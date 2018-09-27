# -*- coding: utf-8 -*-
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

class MyLineEdit(QtGui.QLineEdit,QtCore.QObject):
    clicked = QtCore.pyqtSignal() # signal when the text entry is left clicked
    focused = QtCore.pyqtSignal()

    def __init__(self, value):

        super(MyLineEdit, self).__init__(value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: self.clicked.emit()
        else: super().mousePressEvent(event)

    def focusInEvent(self,event):
        super(MyLineEdit, self).focusInEvent(event)
        self.focused.emit()

    # def connectNotify(self,signal):
    #     print("test")
    #     print(signal)
    #     print(dir(signal))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.MainWindow.setMinimumSize(600, 320) #290)
        self.MainWindow.setMaximumSize(800, 320)
        self.MainWindow.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        # self.MainWindow.setStyleSheet("margin: 0px; border: 2px solid green;") # padding: 20px;") # background-color:grey;


        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        # self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))

        self.scrollArea.setStyleSheet('QWidget#scrollArea {border: 0px;}')
        # self.scrollArea.setStyleSheet("border: 0px;") # padding: 20px;") # background-color:grey;
        self.scrollArea.setWidget(QtGui.QWidget(self.centralwidget))
        self.scrollArea_layout = QtGui.QVBoxLayout(self.scrollArea.widget())
        self.scrollArea_layout.setMargin(0)
        self.scrollArea_layout.setSpacing(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMaximumSize(800,600)
        self.scrollArea_layout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize) #QLayout.SetFixedSize)
        # setBackground(self.scrollArea, color_frame)

        self.verticalLayout.addWidget(self.scrollArea) #,0, QtCore.Qt.AlignTop)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignTop) 
        ###########################################################################################
        self.layout_path = FrameLayout(self.centralwidget,title="Path")
        self.layout_path.setObjectName('Path')  

        # setBackground(self.layout_path, color_frame)

        self.grpBox_Path = QtGui.QGroupBox(self.layout_path)
        # setBackground(self.grpBox_Path, color_grpBox)

        font = QtGui.QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.grpBox_Path.setFont(font)
        self.grpBox_Path.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.grpBox_Path.setFlat(False)
        self.grpBox_Path.setCheckable(False)
        self.grpBox_Path.setObjectName(_fromUtf8("grpBox_Path"))
        self.gridLayout = QtGui.QGridLayout(self.grpBox_Path)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btn_output = QtGui.QPushButton(self.grpBox_Path)
        self.btn_output.setFixedWidth(30)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.btn_output.setFont(font)
        self.btn_output.setObjectName(_fromUtf8("btn_output"))
        self.gridLayout.addWidget(self.btn_output, 2, 2, 1, 1)
        self.lineEdit_mesh = QtGui.QTextEdit(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_mesh.setFont(font)
        self.lineEdit_mesh.setTabChangesFocus(False)
        self.lineEdit_mesh.setReadOnly(True)
        self.lineEdit_mesh.setObjectName(_fromUtf8("lineEdit_mesh"))
        self.gridLayout.addWidget(self.lineEdit_mesh, 1, 1, 1, 1)
        self.btn_scene = QtGui.QPushButton(self.grpBox_Path)
        self.btn_scene.setFixedWidth(30)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.btn_scene.setFont(font)
        self.btn_scene.setCheckable(False)
        self.btn_scene.setObjectName(_fromUtf8("btn_scene"))
        self.gridLayout.addWidget(self.btn_scene, 0, 2, 1, 1)
        self.lineEdit_output = QtGui.QLineEdit(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_output.setFont(font)
        self.lineEdit_output.setReadOnly(True)
        self.lineEdit_output.setObjectName(_fromUtf8("lineEdit_output"))
        self.gridLayout.addWidget(self.lineEdit_output, 2, 1, 1, 1)
        self.lineEdit_scene = QtGui.QLineEdit(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_scene.setFont(font)
        self.lineEdit_scene.setText(_fromUtf8(""))
        self.lineEdit_scene.setReadOnly(True)
        self.lineEdit_scene.setObjectName(_fromUtf8("lineEdit_scene"))
        self.gridLayout.addWidget(self.lineEdit_scene, 0, 1, 1, 1)
        self.label_mesh = QtGui.QLabel(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_mesh.setFont(font)
        self.label_mesh.setObjectName(_fromUtf8("label_mesh"))
        self.gridLayout.addWidget(self.label_mesh, 1, 0, 1, 1)
        self.label_output = QtGui.QLabel(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_output.setFont(font)
        self.label_output.setObjectName(_fromUtf8("label_output"))
        self.gridLayout.addWidget(self.label_output, 2, 0, 1, 1)
        self.label_scene = QtGui.QLabel(self.grpBox_Path)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_scene.setFont(font)
        self.label_scene.setObjectName(_fromUtf8("label_scene"))
        self.gridLayout.addWidget(self.label_scene, 0, 0, 1, 1)
        self.btn_mesh = QtGui.QPushButton(self.grpBox_Path)
        self.btn_mesh.setFixedWidth(30)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.btn_mesh.setFont(font)
        self.btn_mesh.setObjectName(_fromUtf8("btn_mesh"))
        self.gridLayout.addWidget(self.btn_mesh, 1, 2, 1, 1)

      
        self.layout_path.addWidget(self.grpBox_Path)
        self.layout_path.toggleCollapsed()

        self.scrollArea_layout.addWidget(self.layout_path) # , 0, QtCore.Qt.AlignTop)


        ###########################################################################################
        self.layout_reductionParam = FrameLayout(self.centralwidget,title="Reduction Parameters")
        self.layout_reductionParam.setObjectName('ReductionParameters')

        # setBackground(self.layout_reductionParam, color_frame)

        self.grpBox_ReductionParam = QtGui.QGroupBox(self.layout_reductionParam)
        self.grpBox_ReductionParam.setEnabled(True)
        

        font = QtGui.QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.grpBox_ReductionParam.setFont(font)
        self.grpBox_ReductionParam.setObjectName(_fromUtf8("grpBox_ReductionParam"))
        self.formLayout = QtGui.QFormLayout(self.grpBox_ReductionParam)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_moduleName = QtGui.QLabel(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_moduleName.setFont(font)
        self.label_moduleName.setObjectName(_fromUtf8("label_moduleName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_moduleName)
        self.lineEdit_moduleName = QtGui.QLineEdit(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_moduleName.setFont(font)
        self.lineEdit_moduleName.setText(_fromUtf8(""))
        self.lineEdit_moduleName.setPlaceholderText(_fromUtf8(""))
        self.lineEdit_moduleName.setObjectName(_fromUtf8("lineEdit_moduleName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEdit_moduleName)
        self.label_NodeToReduce = QtGui.QLabel(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_NodeToReduce.setFont(font)
        self.label_NodeToReduce.setObjectName(_fromUtf8("label_NodeToReduce"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_NodeToReduce)
        self.lineEdit_NodeToReduce = MyLineEdit(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_NodeToReduce.setFont(font)
        self.lineEdit_NodeToReduce.setObjectName(_fromUtf8("lineEdit_NodeToReduce"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_NodeToReduce)
        self.label_AddTranslation = QtGui.QLabel(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_AddTranslation.setFont(font)
        self.label_AddTranslation.setObjectName(_fromUtf8("label_AddTranslation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_AddTranslation)
        self.checkBox_AddTranslation = QtGui.QCheckBox(self.grpBox_ReductionParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.checkBox_AddTranslation.setFont(font)
        self.checkBox_AddTranslation.setText(_fromUtf8(""))
        self.checkBox_AddTranslation.setObjectName(_fromUtf8("checkBox_AddTranslation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.checkBox_AddTranslation)
        

        self.layout_reductionParam.addWidget(self.grpBox_ReductionParam)
        self.scrollArea_layout.addWidget(self.layout_reductionParam) #, 0, QtCore.Qt.AlignTop)


        ###########################################################################################
        self.layout_advancedParam = FrameLayout(self.centralwidget,title="Advanced Parameter")
        self.layout_advancedParam.setObjectName('AdvancedParameter')
        # setBackground(self.layout_advancedParam, color_frame)


        self.grpBox_AdvancedParam = QtGui.QGroupBox(self.layout_advancedParam)
        self.grpBox_AdvancedParam.setEnabled(True)
        

        font = QtGui.QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.grpBox_AdvancedParam.setFont(font)
        self.grpBox_AdvancedParam.setObjectName(_fromUtf8("grpBox_AdvancedParam"))
        self.formLayout_2 = QtGui.QFormLayout(self.grpBox_AdvancedParam)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_addToLib = QtGui.QLabel(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_addToLib.setFont(font)
        self.label_addToLib.setObjectName(_fromUtf8("label_addToLib"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_addToLib)
        self.checkBox_addToLib = QtGui.QCheckBox(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.checkBox_addToLib.setFont(font)
        self.checkBox_addToLib.setText(_fromUtf8(""))
        self.checkBox_addToLib.setObjectName(_fromUtf8("checkBox_addToLib"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.checkBox_addToLib)
        self.lineEdit_toKeep = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_toKeep.setFont(font)
        self.lineEdit_toKeep.setObjectName(_fromUtf8("lineEdit_toKeep"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_toKeep)
        self.lineEdit_tolModes = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_tolModes.setFont(font)
        self.lineEdit_tolModes.setText(_fromUtf8(""))
        self.lineEdit_tolModes.setObjectName(_fromUtf8("lineEdit_tolModes"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.lineEdit_tolModes)
        self.label_tolModes = QtGui.QLabel(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_tolModes.setFont(font)
        self.label_tolModes.setObjectName(_fromUtf8("label_tolModes"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_tolModes)
        self.label_toKeep = QtGui.QLabel(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_toKeep.setFont(font)
        self.label_toKeep.setObjectName(_fromUtf8("label_toKeep"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_toKeep)
        self.label_tolGIE = QtGui.QLabel(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.label_tolGIE.setFont(font)
        self.label_tolGIE.setObjectName(_fromUtf8("label_tolGIE"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_tolGIE)
        self.lineEdit_tolGIE = QtGui.QLineEdit(self.grpBox_AdvancedParam)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.lineEdit_tolGIE.setFont(font)
        self.lineEdit_tolGIE.setText(_fromUtf8(""))
        self.lineEdit_tolGIE.setObjectName(_fromUtf8("lineEdit_tolGIE"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.lineEdit_tolGIE)


        self.layout_advancedParam.addWidget(self.grpBox_AdvancedParam)
        self.scrollArea_layout.addWidget(self.layout_advancedParam) #, 0, QtCore.Qt.AlignTop)


        # ###########################################################################################
        # font = QtGui.QFont()
        # font.setPointSize(5)
        # font.setUnderline(False)
        # self.test = FrameLayout(title="TEST")
        # self.test.setObjectName('test')
        # self.test.setFont(font)  
        # self.test.setEnabled(True)
        # self.verticalLayout.addWidget(self.test)
        # # self.grpBox_AnimationParam.setVisible()

        # ###########################################################################################


        ###########################################################################################
        self.layout_aniamationParam = FrameLayout(self.centralwidget,title="Animation Parameters")
        self.layout_aniamationParam.setObjectName('AnimationParameters')
        # setBackground(self.layout_aniamationParam, color_frame)
        
        self.grpBox_AnimationParam = QtGui.QGroupBox(self.layout_aniamationParam)
        self.grpBox_AnimationParam.setEnabled(True)


        font = QtGui.QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.verticalLayout_1 = QtGui.QVBoxLayout(self.grpBox_AnimationParam)
        self.verticalLayout_1.setObjectName(_fromUtf8("verticalLayout_1"))
        self.grpBox_AnimationParam.setFont(font)
        self.grpBox_AnimationParam.setObjectName(_fromUtf8("grpBox_AnimationParam"))
        self.tableWidget_animationParam = QtGui.QTableWidget(self.grpBox_AnimationParam)
        self.verticalLayout_1.addWidget(self.tableWidget_animationParam)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.tableWidget_animationParam.setFont(font)
        self.tableWidget_animationParam.setObjectName(_fromUtf8("tableWidget_animationParam"))
        self.tableWidget_animationParam.setColumnCount(3)
        self.tableWidget_animationParam.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget_animationParam.setHorizontalHeaderItem(2, item)
        self.tableWidget_animationParam.setColumnWidth(0, 90)

        item = QtGui.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget_animationParam.setHorizontalHeaderItem(0, item)
        self.tableWidget_animationParam.setColumnWidth(1, 80)

        item = QtGui.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget_animationParam.setHorizontalHeaderItem(1, item)
        self.tableWidget_animationParam.setColumnWidth(2, 90)

        self.tableWidget_animationParam.verticalHeader().hide()
        self.layout_addRemoveRow = QtGui.QGridLayout()
        self.layout_addRemoveRow.setObjectName(_fromUtf8("layout_addRemoveRow"))

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)
        self.btn_addLine = QtGui.QPushButton(self.grpBox_AnimationParam)
        self.btn_addLine.setFont(font)
        self.btn_addLine.setObjectName(_fromUtf8("btn_addLine"))
        self.btn_removeLine = QtGui.QPushButton(self.grpBox_AnimationParam)
        self.btn_removeLine.setFont(font)
        self.btn_removeLine.setObjectName(_fromUtf8("btn_removeLine"))
        self.layout_addRemoveRow.addWidget(self.btn_removeLine, 1, 2, 1, 1)
        self.layout_addRemoveRow.addWidget(self.btn_addLine, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layout_addRemoveRow.addItem(spacerItem, 1, 0, 1, 1)
        self.verticalLayout_1.addLayout(self.layout_addRemoveRow)


        self.layout_aniamationParam.addWidget(self.grpBox_AnimationParam)       
        self.scrollArea_layout.addWidget(self.layout_aniamationParam) #, 0, QtCore.Qt.AlignTop)


        ###########################################################################################
        self.layout_execution = FrameLayout(self.centralwidget,title="Execution")
        self.layout_execution.setObjectName('Execution')
        # setBackground(self.layout_execution, color_frame)

        
        self.grpBox_Execution = QtGui.QGroupBox(self.layout_execution)
        self.grpBox_Execution.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpBox_Execution)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.grpBox_Execution.setFont(font)
        self.grpBox_Execution.setObjectName(_fromUtf8("grpBox_Execution"))


        #############################
        #### TEST4
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(False)

        self.phase1 = FrameLayout(self.grpBox_Execution,title="Phase 1")
        self.phase1.setObjectName('Phase 1')
        textBrowser = QtGui.QTextBrowser(self.phase1)
        textBrowser.setFont(font)
        textBrowser.setText("Phase 1 Description")
        self.phase1.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        self.phase2 = FrameLayout(self.grpBox_Execution,title="Phase 2")
        self.phase2.setObjectName('Phase 2')
        textBrowser = QtGui.QTextBrowser(self.phase2)
        textBrowser.setFont(font)
        textBrowser.setText("Phase 2 Description")
        self.phase2.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        self.phase3 = FrameLayout(self.grpBox_Execution,title="Phase 3")
        self.phase3.setObjectName('Phase 3')
        textBrowser = QtGui.QTextBrowser(self.phase3)
        textBrowser.setFont(font)
        textBrowser.setText("Phase 3 Description")
        self.phase3.addWidget(textBrowser)

        textBrowser = QtGui.QTextBrowser()
        self.phase4 = FrameLayout(self.grpBox_Execution,title="Phase 4")
        self.phase4.setObjectName('Phase 4')
        textBrowser = QtGui.QTextBrowser(self.phase4)
        textBrowser.setFont(font)
        textBrowser.setText("Phase 4 Description")
        self.phase4.addWidget(textBrowser)
    
        self.verticalLayout_2.addWidget(self.phase1)
        self.verticalLayout_2.addWidget(self.phase2)
        self.verticalLayout_2.addWidget(self.phase3)
        self.verticalLayout_2.addWidget(self.phase4)

        ########################
        self.layout_execution.addWidget(self.grpBox_Execution)
        self.scrollArea_layout.addWidget(self.layout_execution) #, 0, QtCore.Qt.AlignTop)


        ###########################################################################################


        # spacerItem = QtGui.QSpacerItem(20, 60, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        # self.verticalLayout.insertSpacing (-1, 50)

        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)


        self.layout_launchReduction = QtGui.QGridLayout()
        self.layout_launchReduction.setObjectName(_fromUtf8("layout_launchReduction"))
        self.btn_launchReduction = QtGui.QPushButton(self.centralwidget)
        self.btn_launchReduction.setObjectName(_fromUtf8("btn_launchReduction"))
        self.layout_launchReduction.addWidget(self.btn_launchReduction, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layout_launchReduction.addItem(spacerItem, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.layout_launchReduction)
        # self.layout_launchReduction.setStyleSheet("background-color:black;")


        self.MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtGui.QMenuBar(self.MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 676, 19))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuSettings = QtGui.QMenu(self.menuBar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        self.MainWindow.setMenuBar(self.menuBar)
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


        self.retranslateUi(self.MainWindow)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

        self.setMaximumSize(800,600+65)
        self.setMinimumSize(600, 320) #290)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.grpBox_Path.setTitle(_translate("MainWindow", "", None))
        self.btn_output.setText(_translate("MainWindow", "...", None))
        # self.lineEdit_mesh.setPlaceholderText(_translate("MainWindow", "select all the meshes that your Sofa scene need, they will be copied and put in a mesh folder in the output folder", None))
        self.btn_scene.setText(_translate("MainWindow", "...", None))
        self.lineEdit_output.setPlaceholderText(_translate("MainWindow", "Choose in which folder all the outputs will be placed", None))
        self.lineEdit_scene.setPlaceholderText(_translate("MainWindow", "Choose your sofa scene you want to reduce (.scn/.py/.pyscn)", None))
        self.label_mesh.setText(_translate("MainWindow", "mesh", None))
        self.label_output.setText(_translate("MainWindow", "Output", None))
        self.label_scene.setText(_translate("MainWindow", "Scene", None))
        self.btn_mesh.setText(_translate("MainWindow", "...", None))
        self.grpBox_ReductionParam.setTitle(_translate("MainWindow", "", None))
        self.label_moduleName.setText(_translate("MainWindow", "Module Name", None))
        self.label_NodeToReduce.setToolTip(_translate("MainWindow", "paths to models to reduce", None))
        self.label_NodeToReduce.setText(_translate("MainWindow", "Node To Reduce", None))
        self.lineEdit_NodeToReduce.setPlaceholderText(_translate("MainWindow", "/path/ofMy/sofaNode/inMyScene", None))
        self.label_AddTranslation.setToolTip(_translate("MainWindow", "allow translation along [x,y,z] axis of our reduced model", None))
        self.label_AddTranslation.setText(_translate("MainWindow", "Add Translation", None))
        self.label_addToLib.setText(_translate("MainWindow", "Add to lib", None))
        self.label_tolModes.setToolTip(_translate("MainWindow", "tolerance applied to choose the modes", None))
        self.label_tolModes.setText(_translate("MainWindow", "Tolerance Modes", None))
        self.label_toKeep.setText(_translate("MainWindow", "To keep", None))
        self.label_tolGIE.setToolTip(_translate("MainWindow", "tolerance applied to calculated GIE", None))
        self.label_tolGIE.setText(_translate("MainWindow", "Tolerance GIE", None))
        item = self.tableWidget_animationParam.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "to Animate", None))
        item = self.tableWidget_animationParam.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "animation function", None))
        item = self.tableWidget_animationParam.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "parameters", None))
        # self.tableWidget_animationParam.horizontalHeader().setResizeMode(1, Qt ui.QHeaderView.Stretch)
        # self.tableWidget_animationParam.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
        self.tableWidget_animationParam.horizontalHeader().setStretchLastSection(True)

        self.btn_addLine.setText(_translate("MainWindow", "Add", None))
        self.btn_removeLine.setText(_translate("MainWindow", "Remove", None))

        self.tableWidget_animationParam.resizeColumnsToContents()


        self.btn_launchReduction.setText(_translate("MainWindow", "Launch Reduction", None))
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

def setBackground(obj,color):
    obj.setStyleSheet("background-color: "+color+";")

class EditButtonsWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(EditButtonsWidget,self).__init__(parent)

        # add your buttons
        layout = QtGui.QHBoxLayout()

        # adjust spacings to your needs
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # add your buttons
        layout.addWidget(QtGui.QLabel("toDo"))
        layout.addWidget(QtGui.QPushButton('reset'))

        self.setLayout(layout)


        # #############################
        # #### TEST1
        # self.treeWidget = QtGui.QTreeWidget(self.grpBox_Execution)
        # self.verticalLayout_2.addWidget(self.treeWidget)

        # self.treeWidget.setEnabled(True)
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # font.setUnderline(False)
        # self.treeWidget.setFont(font)
        # self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        # self.treeWidget.setColumnCount(3)
        # self.treeWidget.setHeaderLabels(["phase","state","function"])


        # self.phase1 = QtGui.QTreeWidgetItem(self.treeWidget,["1","ToDo","bablabla"])
        # self.phase1.setCheckState(0, QtCore.Qt.Unchecked)

        # self.phase2 = QtGui.QTreeWidgetItem(self.phase1,["2","ToDo","bablabla"])
        # self.phase2.setCheckState(0, QtCore.Qt.Unchecked)

        # self.phase3 = QtGui.QTreeWidgetItem(self.phase2,["3","ToDo","bablabla"])
        # self.phase3.setCheckState(0, QtCore.Qt.Unchecked)

        # self.phase4 = QtGui.QTreeWidgetItem(self.phase3,["4","ToDo","bablabla"])
        # self.phase4.setCheckState(0, QtCore.Qt.Unchecked)

        # self.treeWidget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        # # self.treeWidget.header().setStretchLastSection(False)
        # self.treeWidget.setColumnWidth(0, 120)
        # self.treeWidget.setColumnWidth(1, 40)
        # # self.treeWidget.horizontalScrollBar().setDisabled(True);
        # # self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff);

        # #############################
        # #### TEST2
        # self.tableWidget_execution = QtGui.QTableWidget(self.grpBox_Execution)

        # font = QtGui.QFont()
        # font.setPointSize(10)
        # font.setUnderline(False)
        # self.tableWidget_execution.setFont(font)
        # self.tableWidget_execution.setObjectName(_fromUtf8("tableWidget_execution"))
        # self.tableWidget_execution.setColumnCount(3)
        # self.tableWidget_execution.setRowCount(0)

        # item = QtGui.QTableWidgetItem()
        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setWeight(75)
        # item.setFont(font)
        # self.tableWidget_execution.setHorizontalHeaderItem(0, item)
        # self.tableWidget_execution.setColumnWidth(1, 80)

        # item = QtGui.QTableWidgetItem()
        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setWeight(75)
        # item.setFont(font)
        # self.tableWidget_execution.setHorizontalHeaderItem(1, item)
        # self.tableWidget_execution.setColumnWidth(2, 90)

        # item = QtGui.QTableWidgetItem()
        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setWeight(75)
        # item.setFont(font)
        # self.tableWidget_execution.setHorizontalHeaderItem(2, item)
        # self.tableWidget_execution.setColumnWidth(0, 90)

        # # self.tableWidget_execution.verticalHeader().hide()

        # self.tableWidget_execution.insertRow(self.tableWidget_execution.rowCount())
        # self.check = QtGui.QCheckBox()
        # self.tableWidget_execution.setCellWidget(0,0,self.check)
        # self.tableWidget_execution.setCellWidget(0,2,EditButtonsWidget())
        # # self.tableWidget_execution.cellWidget(0,2).setText("toDo")
        # self.label = QtGui.QLabel()

        # self.verticalLayout_2.addWidget(self.tableWidget_execution)


        # #############################
        # #### TEST3
        # self.form = QtGui.QTabWidget(self.centralwidget)
        # self.form.setObjectName(_fromUtf8("form"))

        # self.MainParameters = QtGui.QWidget()
        # self.MainParameters.setObjectName(_fromUtf8("MainParameters"))
        # self.form.addTab(self.MainParameters, _fromUtf8(""))
        # self.form.setTabText(self.form.indexOf(self.MainParameters), _translate("MainWindow", "1) Main Parameters", None))

        # self.AdvancedSettings = QtGui.QWidget()
        # self.AdvancedSettings.setObjectName(_fromUtf8("AdvancedSettings"))
        # self.form.addTab(self.AdvancedSettings, _fromUtf8(""))
        # self.form.setTabText(self.form.indexOf(self.AdvancedSettings), _translate("MainWindow", "2) Advanced Settings", None))

        # self.verticalLayout_2.addWidget(self.form)