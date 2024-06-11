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
**Module describing all the functionnalities of MOR GUI**
'''
#######################################################################
####################       IMPORT           ###########################
import os, sys, ast
import glob
import yaml
import contextlib


from pydoc import locate
from subprocess import Popen, PIPE, call


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow



path = os.path.dirname(os.path.abspath(__file__))

try:
    import imp
    imp.find_module('mor')
except:
    sys.path.append(path+'/../../') # TEMPORARY
    # raise ImportError("You need to give to PYTHONPATH the path to the python folder\n"\
    #                  +"of the modelorderreduction plugin in order to use this utility\n"\
    #                  +"Enter this command in your terminal (for temporary use) or in your .bashrc to resolve this:\n"\
    #                  +"export PYTHONPATH=/PathToYourMOR/python")

#### MOR IMPORT ####
# This file holds our MainWindow and all design related things
from mor.gui import ui_design
# Colors specifications 
from mor.gui.settings.ui_colors import *
from mor.gui.settings import existingAnimation as anim

# gui custom widget
from mor.gui.widget import Completer
from mor.gui.widget import TreeModel
from mor.gui.widget import GenericDialogForm
from mor.gui.widget import widgetUtility
# To do reduction
from mor.reduction import ReduceModel
from mor.reduction.container import ObjToAnimate
# Gui usefull fct
from mor.gui import utility as u
# Extract graph from SOFA scene 
from mor.utility import graphScene

#######################################################################

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class UI_mor(QMainWindow, ui_design.Ui_MainWindow):
    def __init__(self):
        # Init of inherited class 
        super(self.__class__, self).__init__()

        # Create each Object & Widget of the interface as an Derived Attribute of QMainWindow
        # to be able to display them
        self.setupUi(self)

        # APP SIGNALS
        self.initSignals()

        # Init validator
        self.initValuesValidator()

        # Init setting
        self.settings = QtCore.QSettings("ModelOrderReduction", "settings")

        # Variable which will contain a compact representation of the graphScene
        self.cfg = None

        # Take current execution path and set it as default when asking for other file
        u.setShortcut([self.lineEdit_scene,self.lineEdit_output])

        # Set max/min size for animation table
        self.tab_animation.resizeTab()

        # Will load setting saved from system if saved once
        self.loadPreferences()

        # Will be set to the current config we are working to avoid
        # asking user each time is saving on which file he want to save it to
        self.saveFile = None


    def initSignals(self):

        # QLineEdit Action
        self.lineEdit_tolModes.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_tolGIE.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_NodeToReduce.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_scene.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_scene.textChanged.connect(lambda: self.importScene(str(self.lineEdit_scene.text()) ) )
        self.lineEdit_output.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_output.textChanged.connect(self.checkPhases)
        self.lineEdit_animationPath.textChanged.connect(lambda: u.check_state(self.sender()))
        self.lineEdit_NodeToReduce.leftArrowBtnClicked.connect(lambda: u.left(self.lineEdit_NodeToReduce))


        # QPushButton Action
        self.btn_scene.clicked.connect(lambda: u.openFileName('Select the SOFA scene you want to reduce',display=self.lineEdit_scene))
        self.btn_output.clicked.connect(lambda: u.openDirName('Select the directory that will contain all the results',display=self.lineEdit_output))
        self.btn_animationPath.clicked.connect(lambda: u.openFileName('Select the python file containing your animation function',display=self.lineEdit_animationPath))
        self.btn_addLine.clicked.connect(lambda: self.tab_animation.addLine(self.cfg))
        self.btn_addLine.clicked.connect(lambda: self.updatePhasesToExecute())
        self.btn_removeLine.clicked.connect(lambda: self.tab_animation.removeLine())
        self.btn_removeLine.clicked.connect(lambda: self.updatePhasesToExecute())

        self.btn_launchReduction.clicked.connect(self.execute)
        self.btn_test1.clicked.connect(lambda: self.testAnimation(template="phase1_snapshots.py"))
        self.btn_test2.clicked.connect(lambda: self.testAnimation(template="phase2_prepareECSW.py"))
        self.btn_debug1.clicked.connect(lambda: self.executeSofaScene(str(self.lineEdit_output.text())+"/debug/debug_scene.py"))
        self.btn_debug2.clicked.connect(lambda: self.executeSofaScene(str(self.lineEdit_output.text())+"/debug/debug_scene.py",param=["--argv",str(self.lineEdit_output.text())+"/debug/step2_stateFile.state"]))
        self.btn_results.clicked.connect(lambda: self.executeSofaScene(str(self.lineEdit_output.text())+"/reduced_"+str(self.lineEdit_moduleName.text())+".py"))
        for i,item in enumerate(self.phaseItem):
            # Actions
            checkBox,btn = item
            checkBox.stateChanged.connect(lambda _, phase=self.phases[i],index=i: widgetUtility.updatePhasesState(index,phase,self.phaseItem))
            btn.clicked.connect(lambda _, btn=btn,checkBox=checkBox: u.greyOut(btn,[checkBox]))

        # QAction Menu Action
        self.actionOpen.triggered.connect(lambda: self.open('Select Config File'))
        self.actionSave_as.triggered.connect(self.saveAs)
        self.actionSave.triggered.connect(self.save)
        self.actionReset.triggered.connect(self.reset)
        self.actionDoc.triggered.connect(lambda: u.openLink("https://modelorderreduction.readthedocs.io/en/latest/"))
        self.actionWebsite.triggered.connect(lambda: u.openLink("https://project.inria.fr/modelorderreduction/"))
        self.actionGithub.triggered.connect(lambda: u.openLink("https://github.com/SofaDefrost/ModelOrderReduction"))


        # QCheckBox
        self.checkBox_auto.stateChanged.connect(lambda: u.greyOut(self.checkBox_auto,[self.lineEdit_phasesToExecute],checked=False))
        self.checkBox_auto.stateChanged.connect(lambda: self.updatePhasesToExecute())


        # Layout
        for layout in self.listLayout:
            layout._title_frame.c.clicked.connect(self.resizeHeight)

    def initValuesValidator(self):

        self.existingAnimation = anim.existingAnimation.copy()

        var_int = '\d{1,10}'
        var_float ="[0-9]{,10}.?[0-9]{1,10}"
        var_semantic = "[a-z|A-Z|\d|\\-|\\_]{1,20}" # string with max 20 char & min 1 with char from a to z/A to Z/-/_
        var_entry = var_semantic+"\\="+var_semantic # string of 2 var_semantic separated by '='
        var_all = "[^\\*]"

        double_validator = QtGui.QDoubleValidator()
        double_validator.setLocale(QtCore.QLocale("en_US"))


        for animation in self.existingAnimation:
            for item in self.existingAnimation[animation]:
                argDefault = self.existingAnimation[animation][item]
                argValidator = None
                if isinstance(argDefault,int):
                    argValidator = (var_int,locate('int'))
                elif isinstance(argDefault,float):
                    argValidator = (double_validator,locate('float'))
                elif isinstance(argDefault,str):
                    argValidator = (var_semantic,locate('str'))
                else:
                    print("ERROR animation")
                self.existingAnimation[animation][item] = [argDefault,argValidator]

        # Update existingAnimation of tab_animation
        self.tab_animation.existingAnimation = self.existingAnimation 

        # Create some QRegExp that we will be used to create Validator
        # allowing us to block certain entry for the user
        self.exp_var = QtCore.QRegExp("^("+var_semantic+")$")
        self.exp_path = QtCore.QRegExp("^("+var_semantic+"){1}(\\/"+var_semantic+")*$")
        self.exp_all = QtCore.QRegExp("^("+var_all+")+$")

        # Add Validator
        self.lineEdit_tolModes.setValidator(double_validator)
        self.lineEdit_tolGIE.setValidator(double_validator)
        self.lineEdit_moduleName.setValidator(QtGui.QRegExpValidator(self.exp_var))
        self.lineEdit_NodeToReduce.setValidator(QtGui.QRegExpValidator(self.exp_path))
        self.lineEdit_scene.setValidator(QtGui.QRegExpValidator(self.exp_all))
        self.lineEdit_output.setValidator(QtGui.QRegExpValidator(self.exp_all))
        self.lineEdit_animationPath.setValidator(QtGui.QRegExpValidator(self.exp_all))

        self.preferenceKey = {'verbose':[False,(double_validator,locate('bool'))],
                         'nbrCPU':[2,(QtGui.QIntValidator(),locate('int'))]}

        self.dialogMenu = GenericDialogForm("Preferences",self.preferenceKey)

    def closeEvent(self, event):
        settings = self.settings
        settings.setValue("lastsession", path+'/settings/last_ui_cfg.yml')

        # this writes the settings to storage
        del settings

        self.saveFile = path+'/settings/last_ui_cfg.yml'
        self.save()

        event.accept()

    def resizeEvent(self, event):

        height = 600+65
        # print(self.width(),self.height())
        self.setMaximumSize(800,height)
        self.setMinimumSize(630, 320) #290)
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def resizeHeight(self,offset=145):
        # print("resizeHeight ------------------>")

        height = offset
        for layout in self.listLayout:

            if layout._is_collasped:
                if layout.height() > 30 :
                    layout.resize(layout.width(),30)
                height += 30
            else:
                height += layout.height()


        # self.scrollArea.resize(self.scrollArea.width(),height)
        if height > 600:
            self.resize(self.width(),600+65)
        else:
            self.resize(self.width(),height+20)

    def loadPreferences(self):

        settings = QtCore.QSettings("ModelOrderReduction", "settings")
        tmp = {}
        for key , value in self.preferenceKey.items():
            dataType = value[1][1]
            tmp[key] = settings.value(key, type=dataType)
            # quick and dirty fix, need to implement default value in GenericDialogForm
            # & be able to forbid putting negative or to high cpu number
            if (key == 'nbrCPU'):
                if (tmp[key]<1):
                    tmp[key] = 1

        if (settings.value("lastsession", type=str)):
            with contextlib.suppress(Exception):
                self.load(settings.value("lastsession", type=str))
        else:
            # Set global App user fields to blank config
            self.reset(state=False)

        self.dialogMenu.load(tmp)

    @QtCore.pyqtSlot(bool)
    def on_actionPreferences_triggered(self, triggered):
        settings = self.settings
        # default_config_value = settings.value("test", defaultValue=None, type=str)

        # preference_dialog = PreferencesDialog(default_config_value=default_config_value, parent=self)
        if self.dialogMenu.exec_():
            for key , value in self.dialogMenu.currentValues.items():
                settings.setValue(key, value)

            # this writes the settings to storage
            del settings

    def updatePhasesToExecute(self):
        if(self.checkBox_auto.isChecked()):
            tmp = u.generatePhaseToExecute(self.tab_animation.rowCount())
            self.lineEdit_phasesToExecute.setText(str(tmp))

    def setEnablePhases(self,state=True):

        for layout in self.listLayout[1:]:
            if not state and layout.collapsed:
                layout.toggleCollapsed()
            layout.setEnabled(state)

        self.btn_launchReduction.setEnabled(state)

    def checkPhases(self):
        # print("checkPhases")
        if str(self.lineEdit_output.text()) != '':
            # print(self.lineEdit_output.text())
            path = self.lineEdit_output.text()
            phasesFile = [
                        ["/debug/debug_scene.py","/debug/stateFile.state"],
                        ["/data/modes.txt"],
                        ["/debug/reducedFF_*","/debug/*_elmts.txt"], #["/debug/step2_stateFile.state",
                        ["/data/*_RID.txt","/data/*_weight.txt","/reduced_*"]
                    ]

            def check(file,item):
                checkBox , btn = item
                try:
                    f = open(file,'r')
                    if f:
                        # print(file+" NOT EMPTY")
                        # item.setExpanded(True)
                        # print("isTristate ",checkBox.isTristate())

                        checkBox.setCheckState(True)
                        checkBox.setDisabled(True)
                        btn.setDisabled(False)
                        checkBox.setTristate(False)
                        # print("isTristate ",checkBox.isTristate())


                        # item.setText(1,"Done")
                    else:
                        # print(file+" EMPTY")
                        # item.setExpanded(False)
                        checkBox.setCheckState(False)
                        checkBox.setDisabled(False)
                        # item.setText(1,"ToDo")
                        return

                # except IOError as (errno, strerror):
                #     print("I/O error({0}): {1}".format(errno, strerror))
                except IOError as error:
                    print('I/O error occurred: {}'.format(error))
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise

            def test(phase,item,globing=False):
                checkBox , btn = item
                for file in phase:
                    # print(item.text(0))
                    if globing:
                        files = glob.glob(str(path+file))
                        # print(file,files)
                        if files:
                            for file in files:
                                # print(file)
                                check(file,item)
                        else:
                            # print(path+file+" NONE")
                            # item.setExpanded(False)
                            checkBox.setCheckState(False)
                            checkBox.setDisabled(False)
                            # item.setText(1,"ToDo")

                            return False

                    else:
                        if os.path.exists(path+file):
                            check(path+file,item)
                        else:
                            # print(path+file+" NONE")
                            # item.setExpanded(False)
                            checkBox.setCheckState(False)
                            checkBox.setDisabled(False)
                            # item.setText(1,"ToDo")
                            return False

            def checkExecution(phases,phaseItem,globing=False):
                for phase in phases :
                    item = phaseItem[phases.index(phase)]
                    state = test(phase,item,globing)
                    if state and state == False:
                        return

            checkExecution(phasesFile[:2],self.phaseItem[:2])
            checkExecution(phasesFile[2:],self.phaseItem[2:],globing=True)

            self.setEnablePhases()

    def reset(self,state=False):
        '''
        Reset (with ctrl+R) application to a 'blank' state
        '''
        self.setEnablePhases(state)
        while self.tab_animation.rowCount() != 0:
            self.tab_animation.removeLine()
        self.saveFile = None
        self.animationDialog = []
        self.load(path+"/settings/reset.yml")

    def save(self):
        '''
        Save (with ctrl+S) application current state as an YAML file
        '''
        if not self.saveFile:
            self.saveAs()
            if not self.saveFile:
                return

        data = {}
        for page in self.grpBoxes:
            if str(page.objectName()) == 'grpBox_Execution':
                data[str(page.objectName())] = {}
                for phase in self.phases:
                    self.buildDic(phase._title_frame,data[str(page.objectName())],str(phase.objectName()))
            else:
                self.buildDic(page,data)

        with open(self.saveFile, 'w') as ymlfile:
            yaml.dump(data,ymlfile, default_flow_style=False)

    def saveAs(self):
        '''
        Save As, ask user .yml file to save & correct name if need be 
        '''
        # self.saveFile = u.openFileName('Save Configuration',"yaml file *.yml")
        self.saveFile, *_ = QtWidgets.QFileDialog.getSaveFileName(self,
            'Save Configuration',filter="yaml file *.yml",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if self.saveFile:
            if self.saveFile.find('.') == -1 :
                self.saveFile = self.saveFile+'.yml'
            if self.saveFile.split('.')[-1] != 'yml':
                self.saveFile = self.saveFile+'.yml'

            self.save()

    def open(self,hdialog,filter='(*.yml)'):
        '''
        Open (with ctrl+O) ask user to choose a file then load it
        '''
        name = u.openFileName(hdialog,filter)
        if name:
            # self.reset(state=True)
            self.load(name)
            self.saveFile = name
            u.setShortcut([self.lineEdit_scene,self.lineEdit_output])

    def importScene(self,filePath):
        if str(self.lineEdit_scene.text()) != '':
            print('Scene to perform reduction on : '+str(self.lineEdit_scene.text()))
            print('Testing scene locally:')
            try :
                self.cfg = graphScene.importScene(filePath)
                print('Scene good for reduction, extracting scene graphTree')
            except:
                print("ERROR : did not succeed importing your scene. Check it to resolve any issue and try again")
                self.reset()
                return

            model = TreeModel(self.cfg)
            # print(model.rootItem.itemData)

            completer = Completer(self.lineEdit_NodeToReduce)
            completer.setModel(model)
            completer.setCompletionColumn(0)
            completer.setCompletionRole(QtCore.Qt.DisplayRole)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            # print(model.dumpObjectTree())
            self.lineEdit_NodeToReduce.setCompleter(completer)
            self.lineEdit_NodeToReduce.clicked.connect(completer.complete)
            self.lineEdit_NodeToReduce.focused.connect(completer.complete)
            completer.activated.connect(lambda: u.display(completer))

    def load(self,name):
        '''
        Load will, from a cfg file, set all the values of the datafields application
        It will iterate on each 'page' our application contains & load it 
        '''
        with open(name, 'r') as ymlfile:
            cfg = yaml.load(ymlfile,Loader=yaml.FullLoader)

        for page in self.grpBoxes:
            # print('PAGE : '+str(page.objectName()))
            pageName = str(page.objectName())
            if cfg.get(pageName):
                # print("pageName",pageName)
                self.loadPage(page,cfg[pageName])

        self.checkPhases()

    def loadPage(self,page,cfg):
        '''
        LoadPage will set all corresponding widget value
        For each key in our cfg file (which are the obj names) it will search the corresponding widget
        '''
        for child in page.children():
            objectName = str(child.objectName())
            # print('CHILD : '+objectName)
            if objectName in cfg:
                if cfg[objectName]:
                    if type(child).__name__ == 'FrameLayout':
                        index = self.phases.index(child)
                        if cfg[objectName]['checkBox'] == 'True':
                            self.phaseItem[index][0].setCheckState(True)
                        elif cfg[objectName]['checkBox'] == 'False':
                            self.phaseItem[index][0].setCheckState(False)
                    if type(child).__name__ == 'QLineEdit' or type(child).__name__ == "LineEdit":
                        # print('----------------->'+objectName)
                        child.setText(cfg[objectName])
                    if type(child).__name__ == 'QTextEdit':
                        # print('----------------->'+objectName)
                        child.setText(cfg[objectName])
                    if type(child).__name__ == 'QCheckBox':
                        # print('----------------->'+objectName)
                        if cfg[objectName] == 'True':
                            child.setCheckState(True)
                            child.setTristate(False)
                        elif cfg[objectName] == 'False':
                            child.setCheckState(False)
                    if type(child).__name__ == 'QSpinBox':
                        child.setValue(cfg[objectName])
                    if type(child).__name__ == 'AnimationTableWidget':
                        # print('----------------->'+objectName)
                        # color = str(self.lineEdit_scene.palette().color(QtGui.QPalette.Background).name())
                        # if color != yellow and color != red:
                        for row in range(child.rowCount()):
                            child.removeRow(0)

                        for row in cfg[objectName]:
                            child.addLine(self.cfg,animation=cfg[objectName][row][1])
                            for column in cfg[objectName][row]:
                                # print(cfg[objectName][row][column])
                                if column == 3:
                                    if cfg[objectName][row][column]:
                                        child.cellWidget(row,column).setText(cfg[objectName][row][column])
                                    else :
                                        child.cellWidget(row,column).setText('')
                                        u.setBackColor(child.cellWidget(row,column))
                                elif column == 1:
                                    child.cellWidget(row,column).setCurrentIndex(list(self.existingAnimation.keys()).index(cfg[objectName][row][column]))
                                elif column == 2:
                                    child.animationDialog[row].load(cfg[objectName][row][column])
                                    child.setAnimationParamStr((row,column))
                                    child.setCellColor((row,column))
                                elif column == 0:
                                    if cfg[objectName][row][column] == 'True':
                                        child.cellWidget(row,column).setCheckState(True)
                                    elif cfg[objectName][row][column] == 'False':
                                        child.cellWidget(row,column).setCheckState(False)
                                    child.cellWidget(row,column).setTristate(False)
                        # print(self.tab_animation.width(),self.tab_animation.height())
                        child.phaseSelected()

                elif child in self.mandatoryFields.keys():
                    u.setBackColor(child)
                    if type(child).__name__ == 'QTableWidget':
                        pass
                    else:
                        child.setText('')
                else:
                    child.setText('')

    def buildDic(self,page,data,pageName=None):
        '''
        BuildDic will build a Dictionnary that will describe the state of a 'page' of our application
        '''
        toSave = ['QLineEdit','QTextEdit','QCheckBox','AnimationTableWidget','QSpinBox','LineEdit']
        if not pageName:
            pageName=str(page.objectName())
        data[pageName] = {}
        # print('pageName : '+pageName)
        for child in page.children():
            objectName = str(child.objectName())
            # if type(child).__name__ == "LineEdit":
            #     print(objectName)
            #     print(type(child).__name__)
            if type(child).__name__ in toSave:
                # print('--------------->'+child.objectName())
                if type(child).__name__ == 'QLineEdit' or type(child).__name__ == "LineEdit":
                    data[pageName][objectName] = str(child.text())
                    # print('----------------->'+str(child.text()))
                if type(child).__name__ == 'QTextEdit':
                    data[pageName][objectName] = str(child.toPlainText())
                    # print('----------------->'+str(child.toPlainText()))
                if type(child).__name__ == 'QCheckBox':
                    data[pageName][objectName] = str(child.isChecked())
                    # print('----------------->'+str(child.isChecked()))
                if type(child).__name__ == 'QSpinBox':
                    data[pageName][objectName] = child.value()
                if type(child).__name__ == 'AnimationTableWidget':
                    # data[pageName][child.objectName()] = child.text()
                    # print('----------------->'+objectName)
                    data[pageName][objectName] = {}
                    for row in range(child.rowCount()):
                        rowdata = []
                        data[pageName][objectName][row] = {}
                        for column in range(child.columnCount()):
                            item = child.cellWidget(row,column)
                            # print(column,item)
                            if column == 0:
                                data[pageName][objectName][row][column] = str(item.isChecked())
                            elif column == 1:
                                data[pageName][objectName][row][column] = str(item.currentText())
                            elif column == 2:
                                item = child.item(row,column)
                                if item.text():
                                    dicParam = {}
                                    params = str(item.text()).replace(' ','').split(',')
                                    for param in params:
                                        tmp = param.split('=')
                                        dicParam[tmp[0]] = tmp[1]
                                    data[pageName][objectName][row][column] = dicParam
                                else:
                                    data[pageName][objectName][row][column] = None
                            elif item.text() != '':
                                data[pageName][objectName][row][column] = str(item.text())
                            else:
                                data[pageName][objectName][row][column] = None
        return data

    def executeSofaScene(self,sofaScene,param=[]):

        if os.path.isfile(sofaScene):
            try:
                arg = ["runSofa"]+[sofaScene]+param
                # print(arg)
                a = Popen(arg,stdout=PIPE, stderr=PIPE)

                if self.dialogMenu.currentValues['verbose']:
                    while True:
                        output = a.stdout.readline().decode()
                        if output == '' and a.poll() is not None:
                            break
                        if output:
                            print(output.strip())

            except:
                print("Unable to find runSofa, please add the runSofa location to your PATH and restart sofa-launcher.")
        else:
            print("ERROR    the file you try to launch doesn't exist, you have to execute the phase first")

    def validateReductionParams(self):
        '''
        When the user try to launch reduction iterate over the different mandatory fields of the gui and if their color are 
        yellow or red inform user he has to complete/correct them
        '''

        msg = []
        for field in self.mandatoryFields.keys():
            color = str(field.palette().color(QtGui.QPalette.Background).name())
            if type(field).__name__ == 'QTableWidget':
                for row in range(field.rowCount()):
                    for column in range(field.columnCount()):
                        item = field.cellWidget(row,column)
                        if item:
                            if str(item.palette().color(QtGui.QPalette.Background).name()) in [yellow,red]:
                                color = item.palette().color().name()
                        elif field.item(row,column).background().color().name() in [yellow,red]:
                            color = field.item(row,column).background().color().name()
            if color == yellow or color == red:
                msg.append(field)

        if msg:
            tmp = 'ERROR:\n'
            for field in msg:
                if type(self.mandatoryFields[field]).__name__ == 'FrameLayout':
                    tmp += 'Wrong/Missing Entry    ----------->    '+self.mandatoryFields[field].title()+'\n'
                else:
                    tmp += 'Wrong/Missing Entry    ----------->    '+self.mandatoryFields[field].text()+'\n'

            return tmp

        return None

    def aggregateReductionParams(self,data):        
        '''
        From the dict representing all the data of the gui ordered by pageName 
        select the parameters to do the reduction and build another dict with entry ReduceModel paramemters name
        '''
        arguments = {}
        msg =[]

        # Path Arguments
        pageName = str(self.grpBox_Path.objectName())

        arguments['originalScene'] = data[pageName]['lineEdit_scene']
        arguments['outputDir'] = data[pageName]['lineEdit_output']

        # ReductionParam Arguments
        pageName = str(self.grpBox_ReductionParam.objectName())

        arguments['nodeToReduce'] = '/'+data[pageName]['lineEdit_NodeToReduce']
        if data[pageName]['lineEdit_moduleName']:
            arguments['packageName'] = data[pageName]['lineEdit_moduleName']
        else: u.msg_info(msg,'No Module Name, take defaul')

        if data[pageName]['checkBox_AddTranslation'] == 'True' :
            arguments['addRigidBodyModes'] = [1,1,1]
        else:
            u.msg_info(msg,'No Translation')
            arguments['addRigidBodyModes'] = [0,0,0]

        # AnimationParam Arguments
        pageName = str(self.grpBox_AnimationParam.objectName())

        arguments['listObjToAnimate'] = []
        for row in data[pageName]['tab_animation']:
            animation = data[pageName]['tab_animation'][row][1]
            for key,value in data[pageName]['tab_animation'][row][2].items():
                typ = self.existingAnimation[animation][key][1][1]
                data[pageName]['tab_animation'][row][2][key] = typ(value)
            arguments['listObjToAnimate'].append(ObjToAnimate(  location = data[pageName]['tab_animation'][row][3],
                                                                animFct = data[pageName]['tab_animation'][row][1],
                                                                **data[pageName]['tab_animation'][row][2]) )

        # Advanced Arguments
        pageName = str(self.grpBox_AdvancedParam.objectName())

        arguments['tolModes'] = float(data[pageName]['lineEdit_tolModes'])
        arguments['tolGIE'] = float(data[pageName]['lineEdit_tolGIE'])

        if data[pageName]['checkBox_addToLib'] == 'True':
            arguments['addToLib'] = True
        else:
            u.msg_info(msg,"The Reduced Model won't be added to the library")


        # Preference Arguments
        for key , value in self.dialogMenu.currentValues.items():
            # print(key,type(value))
            arguments[str(key)] = value


        # Verify there aren't more phasesToExecute selected than what is possible
        # and if that's the case replace value phasesToExecute by maximum possible  
        phasesToExecute = ast.literal_eval(self.lineEdit_phasesToExecute.text())
        maxPhasesToExecute = u.generatePhaseToExecute(self.tab_animation.rowCount())
        if(len(phasesToExecute)>len(maxPhasesToExecute)):
            print("WARNING : list of phase to execute bigger than possible actuation combination, generate new one")
            tmp = u.generatePhaseToExecute(self.tab_animation.rowCount())
            self.lineEdit_phasesToExecute.setText(str(tmp))
        # If an additional aniamtionPath is selected put it in listPathToAnimation in order to allow its import in the templated scene  
        if (self.lineEdit_animationPath.text() !=''):
            arguments['listPathToAnimation'] = [self.lineEdit_animationPath.text()]


        return arguments, msg

    def execute(self):
        '''
        execute will gather all the argument necessary for the execution
        verify there validity than execute the reduction process based on them
        '''
        parametersIssues = self.validateReductionParams()

        if (parametersIssues):
            print(parametersIssues)
            return
        else:
            data = {}
            for page in self.grpBoxes:
                self.buildDic(page,data)

            arguments, msg = self.aggregateReductionParams(data)

            msg = '\n'.join(msg)
            separator = "---------------------\n"


            print(separator+"EXECUTION INFO :\n"+msg+'\n'+separator)
            # print(arguments)
            reduceMyModel = ReduceModel(**arguments)

            steps = []
            for checkBox , btn in self.phaseItem:
                index = self.phaseItem.index((checkBox,btn))
                if checkBox.checkState() == QtCore.Qt.Checked or checkBox.checkState() == QtCore.Qt.PartiallyChecked:
                    if checkBox.isEnabled() == True:
                        steps.append(index)

            # Verify there aren't more phasesToExecute selected than what is possible
            # and if that's the case replace value phasesToExecute by maximum possible  
            phasesToExecute = ast.literal_eval(self.lineEdit_phasesToExecute.text())
            maxPhasesToExecute = u.generatePhaseToExecute(self.tab_animation.rowCount())
            if(len(phasesToExecute)>len(maxPhasesToExecute)):
                print("WARNING : list of phase to execute bigger than possible actuation combination, generate new one")
                tmp = u.generatePhaseToExecute(self.tab_animation.rowCount())
                self.lineEdit_phasesToExecute.setText(str(tmp))
            # If an additional aniamtionPath is selected put it in listPathToAnimation in order to allow its import in the templated scene  
            if (self.lineEdit_animationPath.text() !=''):
                reduceMyModel.reductionAnimations.listPathToAnimation.append(self.lineEdit_animationPath.text())


            print("STEP : "+str(steps))
            if len(steps) == 4:
                reduceMyModel.performReduction(phasesToExecute=phasesToExecute)
                self.executeSofaScene(str(self.lineEdit_output.text())+"/reduced_"+str(self.lineEdit_moduleName.text())+".py")
            elif len(steps) == 0:
                print("Select a step to perform")
            else:
                for step in steps:
                    try:
                        if step == 0:
                            reduceMyModel.phase1(phasesToExecute=phasesToExecute)
                        elif step == 1:
                            reduceMyModel.phase2()
                        elif step == 2:
                            reduceMyModel.phase3(phasesToExecute=phasesToExecute)
                        elif step == 3:
                            reduceMyModel.phase4()
                            self.executeSofaScene(str(self.lineEdit_output.text())+"/reduced_"+str(self.lineEdit_moduleName.text())+".py")
                    except :
                        print("ERROR : some issue happened during "+step)            
        
            self.checkPhases()

    def testAnimation(self,template="phase1_snapshots.py"):
        
        parametersIssues = self.validateReductionParams()

        if (parametersIssues):
            print(parametersIssues)
            return
        else:
            data = {}
            for page in self.grpBoxes:
                self.buildDic(page,data)

            arguments, msg = self.aggregateReductionParams(data)


            reduceMyModel = ReduceModel(**arguments)
            reduceMyModel.generateTestScene(self.tab_animation.currentPhase,template)

            self.executeSofaScene(reduceMyModel.packageBuilder.debugDir+template)

def main():
    app = QtWidgets.QtWidgets(sys.argv)  # A new instance of QApplication
    gui_mor = UI_mor()  # We set the form to be our ExampleApp (design)
    gui_mor.show()  # Show the form
    app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
