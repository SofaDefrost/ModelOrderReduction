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
    README

    to use this python script you need :

        - bla

        - & blabla
'''
#######################################################################
####################       IMPORT           ###########################
import os
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *

import ui_design  # This file holds our MainWindow and all design related things

import yaml
from collections import OrderedDict
from pydoc import locate

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python') # TO CHANGE

# MOR IMPORT
from mor.script import utility
from mor.script import ReduceModel
from mor.script import ObjToAnimate

#######################################################################

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# var_float = "[\d{0,10}|\\.|\d{0,10}]"
var_int = '\d{1,10}'
var_float ="[0-9]{,10}.?[0-9]{,10}"
var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_


existingAnimation = OrderedDict()
existingAnimation['defaultShaking'] = { 'incr':(var_float,locate('float')),
                                        'incrPeriod':(var_float,locate('float')),
                                        'rangeOfAction':(var_float,locate('float'))}
existingAnimation['shakingSofia'] = {'incr':var_float,
                                     'incrPeriod':var_float,
                                     'rangeOfAction':var_float}
existingAnimation['test'] = {'incr':var_float,
                             'incrPeriod':var_float,
                             'rangeOfAction':var_float}

white = '#f2f1f0'
green = '#c4df9b' 
yellow = '#fff79a'
red = '#f6989d'

def setBackColor(widget,color='#fff79a'):
    widget.setStyleSheet('QLineEdit { background-color: %s }' % color)

class ExampleApp(QtGui.QMainWindow, ui_design.Ui_MainWindow):

    def __init__(self):

        # Init of inherited class 
        super(self.__class__, self).__init__()

        # Create each Object & Widget of the interface as an Derived Attribute of QMainWindow
        # to be able to display them
        self.setupUi(self)

        # Create some QRegExp that we will be used to create Validator
        # allowing us to block certain entry for the user
        var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_
        var_entry = var_semantic+"\\="+var_semantic # string of 2 var_semantic separated by '='
        var_all = "[^\\*]"
        defaultShaking_mask = "(incr\\="+var_float+"){1}(incrPeriod\\="+var_float+"){1}(rangeOfAction\\="+var_float+"){1}"

        self.exp_var = QtCore.QRegExp("^("+var_semantic+")$")
        self.exp_path = QtCore.QRegExp("^(\\/"+var_semantic+")+$")
        self.exp_all = QtCore.QRegExp("^("+var_all+")+$")
        # self.exp_var_entry = QtCore.QRegExp("^("+var_entry_spe+"\\,)*("+var_entry_spe+")$")       

        # Add Signals
        self.lineEdit_tolModes.textChanged.emit(self.lineEdit_tolModes.text())
        self.lineEdit_tolGIE.textChanged.emit(self.lineEdit_tolGIE.text())
        self.lineEdit_moduleName.textChanged.emit(self.lineEdit_moduleName.text())
        self.lineEdit_NodeToReduce.textChanged.emit(self.lineEdit_NodeToReduce.text())
        self.lineEdit_scene.textChanged.emit(self.lineEdit_scene.text())
        self.lineEdit_output.textChanged.emit(self.lineEdit_output.text())
        
        # QLineEdit Action
        self.lineEdit_tolModes.textChanged.connect(self.check_state)
        self.lineEdit_tolGIE.textChanged.connect(self.check_state)
        self.lineEdit_moduleName.textChanged.connect(self.check_state)
        self.lineEdit_NodeToReduce.textChanged.connect(self.check_state)
        self.lineEdit_scene.textChanged.connect(self.check_state)
        self.lineEdit_output.textChanged.connect(self.check_state)

        # QPushButton Action
        self.btn_mesh.setDisabled(True)
        self.btn_scene.clicked.connect(lambda: self.openFileName('Select the SOFA scene you want to reduce',display=self.lineEdit_scene))
        self.btn_output.clicked.connect(lambda: self.openDirName('Select the directory tha will contain all the results',display=self.lineEdit_output))
        self.btn_mesh.clicked.connect(lambda: self.openFilesNames('Select the meshes & visual of your scene',display=self.lineEdit_mesh))
        self.btn_addLine.clicked.connect(lambda: self.addLine(self.tableWidget_animationParam))
        self.btn_removeLine.clicked.connect(self.removeLine)
        self.btn_launchReduction.clicked.connect(self.execute)
        
        # QCheckBox Action
        self.checkBox_mesh.stateChanged.connect(lambda: self.greyOut(self.checkBox_mesh,[self.lineEdit_mesh,self.btn_mesh]))
        self.checkBox_executeAll.stateChanged.connect(lambda: self.executeAll(self.checkBox_executeAll,
                                                                            [   self.checkBox_phase1,
                                                                                self.checkBox_phase2,
                                                                                self.checkBox_phase3,
                                                                                self.checkBox_phase4],
                                                                            checked=False))
        
        # QAction Menu Action
        self.actionOpen.triggered.connect(lambda: self.open('Select Config File'))
        self.actionSave_as.triggered.connect(self.saveAs)
        self.actionSave.triggered.connect(self.save)
        self.actionReset.triggered.connect(self.reset)

        # QTable Action
        self.tableWidget_animationParam.cellClicked.connect(self.showAnimationDialog)
        self.animationDialog = []

        # Add Validator
        self.lineEdit_tolModes.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_tolGIE.setValidator(QtGui.QDoubleValidator())
        self.lineEdit_moduleName.setValidator(QtGui.QRegExpValidator(self.exp_var))
        self.lineEdit_NodeToReduce.setValidator(QtGui.QRegExpValidator(self.exp_path))
        self.lineEdit_scene.setValidator(QtGui.QRegExpValidator(self.exp_all))
        self.lineEdit_output.setValidator(QtGui.QRegExpValidator(self.exp_all))

        # Set Mesh Disable by Default
        self.lineEdit_mesh.setDisabled(True)

        # Set the different pages of our application
        # It will ease the way we iterate on them
        self.pages = [self.MainParameters,self.AdvancedSettings,self.ReductionSteps]

        # Will be set to the current config we are working to avoid 
        # asking user each time is saving on which file he want to save it to
        self.saveFile = None

        # Dictionary containing a 'blank' configuration to be able to reset the application
        self.resetFileName = {
                'AdvancedSettings': 
                    {   'checkBox_verbose': 'False', 
                        'spinBox_numberCPU': 4, 
                        'checkBox_addToLib': 'False', 
                        'lineEdit_tolModes': '0.001',
                        'lineEdit_tolGIE': '0.05',
                        'lineEdit_toKeep': ''}, 
                'ReductionSteps': 
                    {   'checkBox_executeAll': 'False', 
                        'checkBox_phase2': 'False',
                        'checkBox_phase4': 'False',
                        'textEdit_preExecutionInfos': '',
                        'checkBox_phase3': 'False',
                        'checkBox_phase1': 'False'},
                'MainParameters': 
                    {   'lineEdit_NodeToReduce': '',
                        'lineEdit_moduleName': 'myReducedModel',
                        'lineEdit_output': '',
                        'lineEdit_mesh': '',
                        'lineEdit_scene': '',
                        'checkBox_AddTranslation': 'False',
                        'tableWidget_animationParam': {0: {0: None, 1: 'defaultShaking', 2: None, 3: None}},
                        'checkBox_mesh': 'False'}
                }

        self.mandatoryFields = OrderedDict([
                                (self.lineEdit_scene,                self.btn_scene),
                                (self.lineEdit_output,               self.btn_output),
                                (self.lineEdit_NodeToReduce,         self.label_NodeToReduce),
                                (self.tableWidget_animationParam,    self.lanel_animationParam),
                                (self.lineEdit_tolGIE,               self.label_tolGIE),
                                (self.lineEdit_tolModes,             self.label_tolModes)
                                ])

        self.reset()



    def setAnimationParamStr(self,cell,items):
        tmp = ''
        for label,lineEdit in items:
            tmp +=str(label)+'='+str(lineEdit)+','
        cell.setText(tmp[:-1])

    def setCellColor(self,dialog,row,column):
        backgrdColor = QColor()
        if dialog.state:
            backgrdColor.setNamedColor(green)
            self.tableWidget_animationParam.item(row,column).setBackgroundColor(backgrdColor)
        else:
            backgrdColor.setNamedColor(yellow)
            self.tableWidget_animationParam.item(row,column).setBackgroundColor(backgrdColor)

    def showAnimationDialog(self, row, column):
        if column == 3 :
            dialog = self.animationDialog[row]
            if dialog.exec_():
                self.setAnimationParamStr(self.tableWidget_animationParam.item(row,column),dialog.currentValues.iteritems())
                self.setCellColor(dialog,row,column)


    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def reset(self):
        '''
        Reset (with ctrl+R) application to a 'blank' state
        '''
        for page in self.pages:
            pageName = str(page.objectName())
            self.loadPage(page,self.resetFileName[pageName])
        self.saveFile = None

    def save(self):
        '''
        Save (with ctrl+S) application current state as an YAML file
        '''
        if not self.saveFile:
            self.saveAs()

        data = {}
        for page in self.pages:
            self.buildDic(page,data)

        with open(self.saveFile, 'w') as ymlfile:
            yaml.dump(data,ymlfile, default_flow_style=False)

    def saveAs(self):
        '''
        Save As, ask user .yml file to save & correct name if need be 
        '''
        self.saveFile = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Configuration',filter="yaml file *.yml"))

        if self.saveFile.find('.') == -1 :
            self.saveFile = self.saveFile+'.yml'
        if self.saveFile.split('.')[-1] != 'yml':
            self.saveFile = self.saveFile+'.yml'

        self.save()

    def open(self,hdialog,filter='(*.yml)'):
        '''
        Open (with ctrl+O) ask user to choose a file then load it
        '''
        name = self.openFileName(hdialog,filter)
        self.load(name)
        self.saveFile = name

    def loadPage(self,page,cfg):
        '''
        LoadPage will set all coresponding widget value
        For each key in our cfg file (which are the obj names) it will search the coresponding widget
        '''
        for child in page.children():
            if str(child.objectName()) in cfg:
                if cfg[str(child.objectName())]:
                    if type(child).__name__ == 'QLineEdit':
                        # print('----------------->'+str(child.objectName()))
                        child.setText(cfg[str(child.objectName())])
                    if type(child).__name__ == 'QTextEdit':
                        # print('----------------->'+str(child.objectName()))
                        child.setText(cfg[str(child.objectName())])
                    if type(child).__name__ == 'QCheckBox':
                        # print('----------------->'+str(child.objectName()))
                        if cfg[str(child.objectName())] == 'True':
                            child.setCheckState(True)
                        elif cfg[str(child.objectName())] == 'False':
                            child.setCheckState(False)
                    if type(child).__name__ == 'QSpinBox':
                        child.setValue(cfg[str(child.objectName())])
                    if type(child).__name__ == 'QTableWidget':
                        # print('----------------->'+str(child.objectName()))
                        for row in range(child.rowCount()):
                            child.removeRow(0)
                        self.addLine(child,len(cfg[str(child.objectName())]))

                        for row in cfg[str(child.objectName())]:
                            for column in cfg[str(child.objectName())][row]:
                                # print(cfg[str(child.objectName())][row][column])
                                if column == 0:
                                    if cfg[str(child.objectName())][row][column]:
                                        child.cellWidget(row,column).setText(cfg[str(child.objectName())][row][column])
                                    else :
                                        child.cellWidget(row,column).setText('')
                                        self.setBackColor(child.cellWidget(row,column))
                                elif column == 1:
                                    child.cellWidget(row,column).setCurrentIndex(existingAnimation.keys().index(cfg[str(child.objectName())][row][column]))
                                elif column == 2 :
                                    if cfg[str(child.objectName())][row][column]:
                                        child.cellWidget(row,column).setText(cfg[str(child.objectName())][row][column])
                                    else :
                                        child.cellWidget(row,column).setText('')
                                elif column == 3:
                                    self.animationDialog[row].load(cfg[str(child.objectName())][row][column])
                                    self.setAnimationParamStr(self.tableWidget_animationParam.item(row,3),self.animationDialog[row].currentValues.iteritems())
                                    self.setCellColor(self.animationDialog[row],row,3)

                elif child in self.mandatoryFields.keys():
                    self.setBackColor(child)
                    child.setText('')
                else:
                    child.setText('')

    def load(self,name):
        '''
        Load will, from a cfg file, set all the values of the datafields application
        It will iterate on each 'page' our application contains & load it 
        '''
        with open(name, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        for page in self.pages:
            pageName = str(page.objectName())
            self.loadPage(page,cfg[pageName])

    def execute(self):
        '''
        execute will gather all the argument necessary for the execution
        verify there validity than execute the reduction process based on them
        '''
        data = {}
        for page in self.pages:
            self.buildDic(page,data)

        arguments = {}
        
        msg = []
        for field in self.mandatoryFields.keys():
            color = str(field.palette().color(QtGui.QPalette.Background).name())
            if type(field).__name__ == 'QTableWidget':
                for row in range(field.rowCount()):
                    for column in range(field.columnCount()):
                        item = field.cellWidget(row,column)
                        if item:
                            if str(item.palette().color(QtGui.QPalette.Background).name()) in [yellow,red]:
                                color = str(item.palette().color(QtGui.QPalette.Background).name())
                        elif str(field.item(row,column).backgroundColor().name()) in [yellow,red]:
                            color = str(field.item(row,column).backgroundColor().name())
            if color == yellow or color == red:
                msg.append(field)

        if msg:
            tmp = 'ERROR:\n'
            for field in msg:
                tmp += 'Wrong/Missing Entry    ----------->    '+self.mandatoryFields[field].text()+'\n'
            self.textEdit_preExecutionInfos.setText(tmp)

        else:
            msg =[]

            # Main Arguments
            pageName = str(self.MainParameters.objectName())

            arguments['originalScene'] = data[pageName]['lineEdit_scene']
            arguments['outputDir'] = data[pageName]['lineEdit_output']
            arguments['nodesToReduce'] = [data[pageName]['lineEdit_NodeToReduce']]
            arguments['listObjToAnimate'] = []
            for row in data[pageName]['tableWidget_animationParam']:
                animation = data[pageName]['tableWidget_animationParam'][row][1]
                for key,value in data[pageName]['tableWidget_animationParam'][row][3].iteritems():
                    typ = existingAnimation[animation][key][1]
                    data[pageName]['tableWidget_animationParam'][row][3][key] = typ(value)
                arguments['listObjToAnimate'].append(ObjToAnimate(  data[pageName]['tableWidget_animationParam'][row][0],
                                                                    data[pageName]['tableWidget_animationParam'][row][1],
                                                                    data[pageName]['tableWidget_animationParam'][row][2],
                                                                    **data[pageName]['tableWidget_animationParam'][row][3]) )

            if data[pageName]['lineEdit_mesh']:
                arguments['meshes'] = data[pageName]['lineEdit_mesh'].split('\n')
            else: self.msg_warning(msg,'No Mesh specified')

            if data[pageName]['lineEdit_moduleName']:
                arguments['packageName'] = data[pageName]['lineEdit_moduleName']
            else: self.msg_info(msg,'No Module Name, take defaul')

            if data[pageName]['checkBox_AddTranslation'] == 'True' :
                arguments['addRigidBodyModes'] = [1,1,1]
            else: 
                self.msg_info(msg,'No Translation')
                arguments['addRigidBodyModes'] = [0,0,0]


            # Advanced Arguments
            pageName = str(self.AdvancedSettings.objectName())

            arguments['tolModes'] = float(data[pageName]['lineEdit_tolModes'])
            arguments['tolGIE'] = float(data[pageName]['lineEdit_tolGIE'])

            if data[pageName]['lineEdit_toKeep']:
                arguments['toKeep'] = data[pageName]['lineEdit_toKeep']
            else: self.msg_info(msg,'No To Keep Specified, take default')

            if data[pageName]['checkBox_addToLib'] == 'True':
                arguments['addToLib'] = True
            else:
                self.msg_info(msg,"The Reduced Model won't be added to the library")
            
            if data[pageName]['checkBox_verbose'] == 'True':
                arguments['verbose'] = True
            else:
                self.msg_info(msg,'Verbose Set to False')

            if data[pageName]['spinBox_numberCPU']:
                arguments['nbrCPU'] = data[pageName]['spinBox_numberCPU']

            # Execution Arguments
            pageName = str(self.ReductionSteps.objectName())


            msg = '\n'.join(msg)
            self.textEdit_preExecutionInfos.setText(msg)
            separator = "---------------------\n\n"


            if msg.find('ERROR') != -1:
                self.textEdit_preExecutionInfos.append(separator+'Execution Stopped')
            else:
                reduceMyModel = ReduceModel(**arguments)

                if data[pageName]['checkBox_executeAll'] == 'True':
                    self.textEdit_preExecutionInfos.append(separator+'Execute All')
                    reduceMyModel.performReduction()
                else:
                    self.textEdit_preExecutionInfos.setText(msg)
                    if data[pageName]['checkBox_phase1'] == 'True':
                        self.textEdit_preExecutionInfos.append(separator+'Execute Phase 1')
                        reduceMyModel.phase1()
                    if data[pageName]['checkBox_phase2'] == 'True':
                        self.textEdit_preExecutionInfos.append(separator+'Execute Phase 2')
                        reduceMyModel.phase2()
                    if data[pageName]['checkBox_phase3'] == 'True':
                        self.textEdit_preExecutionInfos.append(separator+'Execute Phase 3')
                        reduceMyModel.phase3()
                    if data[pageName]['checkBox_phase4'] == 'True': 
                        self.textEdit_preExecutionInfos.append(separator+'Execute Phase 4')
                        reduceMyModel.phase4()

                self.textEdit_preExecutionInfos.append(separator+'Execution Finished')

    def buildDic(self,page,data):
        '''
        BuildDic will build a Dictionnary that will describe the state of a 'page' of our application
        '''
        toSave = ['QLineEdit','QTextEdit','QCheckBox','QTableWidget','QSpinBox']
        pageName = str(page.objectName())
        data[pageName] = {}

        for child in page.children():
            # print(child.objectName())
            # print(type(child).__name__)
            if type(child).__name__ in toSave:
                # print('--------------->'+child.objectName())
                if type(child).__name__ == 'QLineEdit':
                    data[pageName][str(child.objectName())] = str(child.text())
                    # print('----------------->'+str(child.text()))
                if type(child).__name__ == 'QTextEdit':
                    data[pageName][str(child.objectName())] = str(child.toPlainText())
                    # print('----------------->'+str(child.toPlainText()))
                if type(child).__name__ == 'QCheckBox':
                    data[pageName][str(child.objectName())] = str(child.isChecked())
                    # print('----------------->'+str(child.isChecked()))
                if type(child).__name__ == 'QSpinBox':
                    data[pageName][str(child.objectName())] = child.value()
                if type(child).__name__ == 'QTableWidget':
                    # data[pageName][child.objectName()] = child.text()
                    # print('----------------->'+str(child.objectName()))
                    data[pageName][str(child.objectName())] = {}
                    for row in range(child.rowCount()):
                        rowdata = []
                        data[pageName][str(child.objectName())][row] = {}
                        for column in range(child.columnCount()):
                            item = child.cellWidget(row,column)
                            if column == 1:
                                data[pageName][str(child.objectName())][row][column] = str(item.currentText())
                            elif column == 3:
                                item = child.item(row,column)
                                if item.text():
                                    dicParam = {}
                                    params = str(item.text()).replace(' ','').split(',')
                                    for param in params:
                                        tmp = param.split('=')
                                        dicParam[tmp[0]] = tmp[1]
                                    data[pageName][str(child.objectName())][row][column] = dicParam
                                else:
                                    data[pageName][str(child.objectName())][row][column] = None
                            elif item.text() != '':
                                data[pageName][str(child.objectName())][row][column] = str(item.text())
                            else:
                                data[pageName][str(child.objectName())][row][column] = None
        return data

    def openFileName(self,hdialog,filter="Sofa Scene (*.py *.pyscn)",display=None):
        '''
        openFileName will pop up a dialog window allowing the user to choose a file
        and potentially display the path to it 
        '''
        filename = QtGui.QFileDialog.getOpenFileName(self, hdialog, '.',filter=filter)
        if display:
            display.setText(filename)
        return filename

    def openFilesNames(self,hdialog,display=None):
        '''
        openFilesNames will pop up a dialog window allowing the user to choose multiple files
        and potentially display there coreponding path
        '''
        filesName = QtGui.QFileDialog.getOpenFileNames(self, hdialog, '.', filter="*.stl *.vtu *.vtk")
        if display:
            for fileName in filesName:
                display.append(fileName)
        return filesName

    def openDirName(self,hdialog,display=None):
        '''
        openDirName will pop up a dialog window allowing the user to choose a directory
        and potentially display the path to it 
        '''
        filename = QtGui.QFileDialog.getExistingDirectory(self, hdialog)
        if display:
            display.setText(filename)
        return filename

    def executeAll(self,checkBox,items,checked=True):
        '''
        executeAll is the action associated with checkBox_executeAll
        it will check all the steps while greying them out
        '''
        self.checkedBoxes(checkBox,items,checked)
        self.greyOut(checkBox,items,checked)

    def greyOut(self,checkBox,items,checked=True):
        '''
        greyOut makes items unavailable for the user by greying them out
        '''
        if checkBox.isChecked():
            for item in items:
                item.setDisabled(not checked)
        else:
            for item in items:
                item.setDisabled(checked)

    def checkedBoxes(self,checkBox,items,checked=True):
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

    def addComboToTab(self,tab,values,row,column):
        '''
        addComboToTab will add a QComboBox to an QTableWidget[row][column] and fill it with different value 
        '''
        combo = QtGui.QComboBox()
        combo.setObjectName(_fromUtf8("combo"+str(row)+str(column)))
        combo.activated.connect(lambda: self.addAnimationDialog(tab,row))
        for value in values:
            combo.addItem(value)
        tab.setCellWidget(row,column,combo)

    def addLine(self,tab,number=1):
        for new in range(number):
            tab.insertRow( self.tableWidget_animationParam.rowCount())
            row = tab.rowCount()-1

            tmp = QLineEdit()
            tmp.textChanged.emit(tmp.text())
            tmp.textChanged.connect(self.check_state)
            tmp.setValidator(QtGui.QRegExpValidator(self.exp_var))
            self.setBackColor(tmp)
            tab.setCellWidget(row,0,tmp)


            tmp = QLineEdit()
            tmp.setValidator(QtGui.QRegExpValidator(self.exp_var))
            tab.setCellWidget(row,2,tmp)

            item = QTableWidgetItem()
            self.tableWidget_animationParam.setItem(row,3,item)
            backgrdColor = QColor()
            backgrdColor.setNamedColor(yellow)
            self.tableWidget_animationParam.item(row,3).setBackgroundColor(backgrdColor)


            self.animationDialog.append(Ui_GenericAnimationForm('defaultShaking',existingAnimation['defaultShaking']))

            self.addComboToTab(tab,existingAnimation.keys(),row,1)

    def addAnimationDialog(self,tab,row):
        previousAnimation = self.animationDialog[row].animation
        currentAnimation = str(tab.cellWidget(row,1).currentText())

        if previousAnimation != currentAnimation:
            self.animationDialog[row] = Ui_GenericAnimationForm(currentAnimation,existingAnimation[currentAnimation])
            self.tableWidget_animationParam.item(row,3).setText('')

    def removeLine(self):
        currentRow = self.tableWidget_animationParam.currentRow()
        rowCount = self.tableWidget_animationParam.rowCount()-1
        if currentRow != -1:
            rm = True 
            row = currentRow
        elif rowCount != -1:
            rm = True
            row = rowCount
        else :
            rm = False
        if rm:
            self.tableWidget_animationParam.removeRow(row)
            self.animationDialog.remove(self.animationDialog[row])

    def setBackColor(self,widget,color='#fff79a'):
        widget.setStyleSheet('QLineEdit { background-color: %s }' % color)
    def msg_warning(self,msg,info):
        msg.append("WARNING    "+info)
    def msg_info(self,msg,info):
        msg.append("INFO       "+info)
    def msg_error(self,msg,info):
        msg.append("ERROR      "+info)

###################################################################################################

class Ui_GenericAnimationForm(QtGui.QDialog):
    def __init__(self,animation,param,currentValues=None):
        QtGui.QDialog.__init__(self)

        self.state = False
        self.animation = animation
        self.param = param
        self.row = OrderedDict()
        if not currentValues:
            self.currentValues = {}

        self.setupUi(self)
        self.btn_submit.clicked.connect(self.submitclose)

    def setupUi(self, ShowGroupWidget):
        self.setObjectName(_fromUtf8("Animation Parameters"))
        self.resize(300, 137)
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
            lineEdit.textChanged.connect(self.check_state)
            lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^("+value[0]+")$")))
            setBackColor(lineEdit)

            self.row[label] = lineEdit
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.LabelRole, label)
            self.formLayout_2.setWidget(i, QtGui.QFormLayout.FieldRole, lineEdit)
            i += 1

        self.btn_submit = QtGui.QPushButton(self)
        self.btn_submit.setObjectName(_fromUtf8("btn_submit"))
        self.btn_submit.setText("Ok")
        self.formLayout_2.setWidget(i, QtGui.QFormLayout.FieldRole, self.btn_submit)

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
        if all( lineEdit.palette().color(QtGui.QPalette.Background).name() not in [yellow,red,white] for label,lineEdit in self.row.iteritems()):
            self.state = True

    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)


def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function