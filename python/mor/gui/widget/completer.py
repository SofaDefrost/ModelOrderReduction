# -*- coding: utf-8 -*-
'''
**Class used to create an auto-completion help**
'''
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import Qt
counter = 0

class Completer(QCompleter):
    asChild = False

    def splitPath(self, path):
        # print("path")
        return path.split('/')
    def pathFromIndex(self, index):
        global counter
        self.asChild = False
        if self.model().data(index.child(0,0), Qt.DisplayRole):
            self.asChild = True

        # print(str(counter)+' , '+str(self.model().data(index, Qt.DisplayRole)))
        counter += 1

        result = []
        while index.isValid():
            # print('index.isValid')
            result = [self.model().data(index, Qt.DisplayRole)] + result
            # print('result : ',result)
            index = index.parent()

        r = '/'.join(result)
        # print("COMPLETER RETURN  ------> "+r)
        return r