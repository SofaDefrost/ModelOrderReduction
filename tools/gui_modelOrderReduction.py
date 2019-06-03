# -*- coding: utf-8 -*-
'''
Exemple python file to launch the MOR GUI
'''
import os,sys
from PyQt4 import QtGui

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../python/') # TO CHANGE

from mor.gui.ui_mor import UI_mor

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    gui_mor = UI_mor()  # We set the form to be our ExampleApp (design)
    gui_mor.show()  # Show the form
    app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function