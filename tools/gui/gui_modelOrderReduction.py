# -*- coding: utf-8 -*-
'''
Python file to launch the MOR GUI

TO USE:
    execute it via a terminal
'''
import os,sys
from PyQt5 import QtWidgets

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/../../python/') # TO CHANGE

from mor.gui.ui_mor import UI_mor

def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    gui_mor = UI_mor()  # We set the form to be our ExampleApp (design)
    gui_mor.show()  # Show the form
    app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function