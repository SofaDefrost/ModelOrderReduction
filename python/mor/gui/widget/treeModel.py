# -*- coding: utf-8 -*-
'''
**Class allowing to save elements in a Model Tree**

We use it to store the hierarchy of a SOFA scene 
in order to use it as input of the :py:class:`.Completer`

To init our :py:class:`.TreeModel`,
we get a SOFA Model Tree a scene thanks to :py:func:`.getGraphScene` and give 
and give it as input to our :py:class:`.TreeModel` Class

.. sourcecode:: python

    cfg = graphScene.importScene(filePath)

    model = TreeModel(cfg)
'''
from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractItemModel


class TreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None , obj = False):
        super(TreeModel, self).__init__(parent)

        # self.rootItem = TreeItem(("Region", "Abbreviation"))
        self.rootItem = TreeItem(("GraphScene"))
        self.setupModelData(data, self.rootItem, obj)

    def columnCount(self, parent):
        if parent.isValid():
            # print('columnCount isValid',parent.internalPointer().columnCount())
            return parent.internalPointer().columnCount()
        else:
            # print('columnCount',self.rootItem.columnCount())
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.EditRole:
            return self.rootItem.data(0)

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, dic, parent, obj = False):
        # parents = [parent]
        # # indentations = [0]
        parents = []

        def complete(dic,currentParent,obj=False):
            for key in dic:
                # print('KEY = '+key+'| currentParent = '+currentParent.itemData)
                
                newtreeitem = TreeItem(key, currentParent)
                currentParent.appendChild(newtreeitem)
                
                if newtreeitem not in parents and not obj:
                    parents.append(newtreeitem) 
                
                if dic[key]:
                    if isinstance(dic[key],dict):
                        complete(dic[key],newtreeitem)

        complete(dic["tree"],parent)

        if obj:
            for parent in parents:
                # print(parent.itemData)
                complete(dic["obj"][parent.itemData],parent,True)

class TreeItem(object):
    def __init__(self, data, parent=None):
        # print('TreeItem',data,parent)
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData
    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0
    def __repr__(self):
        return 'TreeItem(%s)' % self.itemData