# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
counter = 0

class MyCompleter(QtGui.QCompleter):
    asChild = False

    def splitPath(self, path):
        # print("path")
        return path.split('/')
    def pathFromIndex(self, index):
        global counter
        self.asChild = False
        if self.model().data(index.child(0,0), QtCore.Qt.DisplayRole):
            self.asChild = True

        # print(str(counter)+' , '+str(self.model().data(index, QtCore.Qt.DisplayRole)))
        counter += 1

        result = []
        while index.isValid():
            # print('index.isValid')
            result = [self.model().data(index, QtCore.Qt.DisplayRole)] + result
            # print('result : ',result)
            index = index.parent()

        r = '/'.join(result)
        # print("COMPLETER RETURN  ------> "+r)
        return r