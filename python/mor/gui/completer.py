# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
counter = 0

class MyCompleter(QtGui.QCompleter):
    asChild = False

    def splitPath(self, path):
        print("path")
        return path.split('/')
    def pathFromIndex(self, index):
        global counter
        self.asChild = False
        if self.model().data(index.child(0,0), QtCore.Qt.DisplayRole):
            self.asChild = True

        print(str(counter)+str(self.model().data(index, QtCore.Qt.DisplayRole)))
        counter += 1

        result = []
        while index.isValid():
            # print('index.isValid')
            result = [self.model().data(index, QtCore.Qt.DisplayRole)] + result
            # print('result : ',result)
            index = index.parent()
        if self.asChild:
            r = '/'.join(result)+'/'
        else:
            r = '/'.join(result)
        print("COMPLETER RETURN")
        return r

    

## QCompleter

# ['CaseInsensitivelySortedModel', 'CaseSensitivelySortedModel', 'CompletionMode', 'InlineCompletion', 
# 'ModelSorting', 'PopupCompletion', 'UnfilteredPopupCompletion', 'UnsortedModel', '__class__', '__delattr__', 
# '__dict__', '__doc__', '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__module__', 
# '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 
# '__weakref__', 'activated', 'blockSignals', 'caseSensitivity', 'childEvent', 'children', 'complete', 'completionColumn', 
# 'completionCount', 'completionMode', 'completionModel', 'completionPrefix', 'completionRole', 'connect', 'connectNotify', 
# 'currentCompletion', 'currentIndex', 'currentRow', 'customEvent', 'deleteLater', 'destroyed', 'disconnect', 'disconnectNotify', 
# 'dumpObjectInfo', 'dumpObjectTree', 'dynamicPropertyNames', 'emit', 'event', 'eventFilter', 'findChild', 'findChildren', 'highlighted', 
# 'inherits', 'installEventFilter', 'isWidgetType', 'killTimer', 'maxVisibleItems', 'metaObject', 'model', 'modelSorting', 'moveToThread', 
# 'objectName', 'parent', 'pathFromIndex', 'popup', 'property', 'pyqtConfigure', 'receivers', 'removeEventFilter', 'sender', 'senderSignalIndex', 
# 'setCaseSensitivity', 'setCompletionColumn', 'setCompletionMode', 'setCompletionPrefix', 'setCompletionRole', 'setCurrentRow', 
# 'setMaxVisibleItems', 'setModel', 'setModelSorting', 'setObjectName', 'setParent', 'setPopup', 'setProperty', 'setWidget', 'setWrapAround', 
# 'signalsBlocked', 'splitPath', 'startTimer', 'staticMetaObject', 'thread', 'timerEvent', 'tr', 'trUtf8', 'widget', 'wrapAround']



## QLineEdit

# ['DrawChildren', 'DrawWindowBackground', 'EchoMode', 'IgnoreMask', 'NoEcho', 'Normal', 'PaintDeviceMetric', 'Password', 
# 'PasswordEchoOnEdit', 'PdmDepth', 'PdmDpiX', 'PdmDpiY', 'PdmHeight', 'PdmHeightMM', 'PdmNumColors', 'PdmPhysicalDpiX', 
# 'PdmPhysicalDpiY', 'PdmWidth', 'PdmWidthMM', 'RenderFlag', 'RenderFlags', '__class__', '__delattr__', '__dict__', '__doc__', 
# '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', 
# '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'acceptDrops', 'accessibleDescription', 
# 'accessibleName', 'actionEvent', 'actions', 'activateWindow', 'addAction', 'addActions', 'adjustSize', 'alignment', 
# 'autoFillBackground', 'backgroundRole', 'backspace', 'baseSize', 'blockSignals', 'changeEvent', 'childAt', 'childEvent', 
# 'children', 'childrenRect', 'childrenRegion', 'clear', 'clearFocus', 'clearMask', 'clicked', 'close', 'closeEvent', 
# 'colorCount', 'completer', 'connect', 'connectNotify', 'contentsMargins', 'contentsRect', 'contextMenuEvent', 
# 'contextMenuPolicy', 'copy', 'create', 'createStandardContextMenu', 'cursor', 'cursorBackward', 'cursorForward', 
# 'cursorMoveStyle', 'cursorPosition', 'cursorPositionAt', 'cursorPositionChanged', 'cursorRect', 'cursorWordBackward', 
# 'cursorWordForward', 'customContextMenuRequested', 'customEvent', 'cut', 'del_', 'deleteLater', 'depth', 'deselect', 'destroy', 
# 'destroyed', 'devType', 'disconnect', 'disconnectNotify', 'displayText', 'dragEnabled', 'dragEnterEvent', 'dragLeaveEvent', 
# 'dragMoveEvent', 'dropEvent', 'dumpObjectInfo', 'dumpObjectTree', 'dynamicPropertyNames', 'echoMode', 'editingFinished', 
# 'effectiveWinId', 'emit', 'enabledChange', 'end', 'ensurePolished', 'enterEvent', 'event', 'eventFilter', 'find', 'findChild', 
# 'findChildren', 'focusInEvent', 'focusNextChild', 'focusNextPrevChild', 'focusOutEvent', 'focusPolicy', 'focusPreviousChild', 
# 'focusProxy', 'focusWidget', 'font', 'fontChange', 'fontInfo', 'fontMetrics', 'foregroundRole', 'frameGeometry', 'frameSize', 
# 'geometry', 'getContentsMargins', 'getTextMargins', 'grabGesture', 'grabKeyboard', 'grabMouse', 'grabShortcut', 'graphicsEffect', 
# 'graphicsProxyWidget', 'handle', 'hasAcceptableInput', 'hasFocus', 'hasFrame', 'hasMouseTracking', 'hasSelectedText', 'height', 
# 'heightForWidth', 'heightMM', 'hide', 'hideEvent', 'home', 'inherits', 'initStyleOption', 'inputContext', 'inputMask', 
# 'inputMethodEvent', 'inputMethodHints', 'inputMethodQuery', 'insert', 'insertAction', 'insertActions', 'installEventFilter', 
# 'isActiveWindow', 'isAncestorOf', 'isEnabled', 'isEnabledTo', 'isEnabledToTLW', 'isFullScreen', 'isHidden', 'isLeftToRight', 
# 'isMaximized', 'isMinimized', 'isModal', 'isModified', 'isReadOnly', 'isRedoAvailable', 'isRightToLeft', 'isTopLevel', 
# 'isUndoAvailable', 'isVisible', 'isVisibleTo', 'isWidgetType', 'isWindow', 'isWindowModified', 'keyPressEvent', 'keyReleaseEvent', 
# 'keyboardGrabber', 'killTimer', 'languageChange', 'layout', 'layoutDirection', 'leaveEvent', 'locale', 'logicalDpiX', 
# 'logicalDpiY', 'lower', 'mapFrom', 'mapFromGlobal', 'mapFromParent', 'mapTo', 'mapToGlobal', 'mapToParent', 'mask', 'maxLength', 
# 'maximumHeight', 'maximumSize', 'maximumWidth', 'metaObject', 'metric', 'minimumHeight', 'minimumSize', 'minimumSizeHint', 
# 'minimumWidth', 'mouseDoubleClickEvent', 'mouseGrabber', 'mouseMoveEvent', 'mousePressEvent', 'mouseReleaseEvent', 'move', 
# 'moveEvent', 'moveToThread', 'nativeParentWidget', 'nextInFocusChain', 'normalGeometry', 'numColors', 'objectName', 
# 'overrideWindowFlags', 'overrideWindowState', 'paintEngine', 'paintEvent', 'paintingActive', 'palette', 'paletteChange', 
# 'parent', 'parentWidget', 'paste', 'physicalDpiX', 'physicalDpiY', 'placeholderText', 'pos', 'previousInFocusChain', 'property', 
# 'pyqtConfigure', 'raise_', 'receivers', 'rect', 'redo', 'releaseKeyboard', 'releaseMouse', 'releaseShortcut', 'removeAction', 
# 'removeEventFilter', 'render', 'repaint', 'resetInputContext', 'resize', 'resizeEvent', 'restoreGeometry', 'returnPressed', 
# 'saveGeometry', 'scroll', 'selectAll', 'selectedText', 'selectionChanged', 'selectionStart', 'sender', 'senderSignalIndex', 
# 'setAcceptDrops', 'setAccessibleDescription', 'setAccessibleName', 'setAlignment', 'setAttribute', 'setAutoFillBackground', 
# 'setBackgroundRole', 'setBaseSize', 'setCompleter', 'setContentsMargins', 'setContextMenuPolicy', 'setCursor', 
# 'setCursorMoveStyle', 'setCursorPosition', 'setDisabled', 'setDragEnabled', 'setEchoMode', 'setEnabled', 'setFixedHeight', 
# 'setFixedSize', 'setFixedWidth', 'setFocus', 'setFocusPolicy', 'setFocusProxy', 'setFont', 'setForegroundRole', 'setFrame', 
# 'setGeometry', 'setGraphicsEffect', 'setHidden', 'setInputContext', 'setInputMask', 'setInputMethodHints', 'setLayout', 
# 'setLayoutDirection', 'setLocale', 'setMask', 'setMaxLength', 'setMaximumHeight', 'setMaximumSize', 'setMaximumWidth', 
# 'setMinimumHeight', 'setMinimumSize', 'setMinimumWidth', 'setModified', 'setMouseTracking', 'setObjectName', 'setPalette', 
# 'setParent', 'setPlaceholderText', 'setProperty', 'setReadOnly', 'setSelection', 'setShortcutAutoRepeat', 'setShortcutEnabled', 
# 'setShown', 'setSizeIncrement', 'setSizePolicy', 'setStatusTip', 'setStyle', 'setStyleSheet', 'setTabOrder', 'setText', 
# 'setTextMargins', 'setToolTip', 'setUpdatesEnabled', 'setValidator', 'setVisible', 'setWhatsThis', 'setWindowFilePath', 
# 'setWindowFlags', 'setWindowIcon', 'setWindowIconText', 'setWindowModality', 'setWindowModified', 'setWindowOpacity', 
# 'setWindowRole', 'setWindowState', 'setWindowTitle', 'show', 'showEvent', 'showFullScreen', 'showMaximized', 'showMinimized', 
# 'showNormal', 'signalsBlocked', 'size', 'sizeHint', 'sizeIncrement', 'sizePolicy', 'stackUnder', 'startTimer', 'staticMetaObject', 
# 'statusTip', 'style', 'styleSheet', 'tabletEvent', 'testAttribute', 'text', 'textChanged', 'textEdited', 'textMargins', 
# 'thread', 'timerEvent', 'toolTip', 'topLevelWidget', 'tr', 'trUtf8', 'underMouse', 'undo', 'ungrabGesture', 'unsetCursor', 
# 'unsetLayoutDirection', 'unsetLocale', 'update', 'updateGeometry', 'updateMicroFocus', 'updatesEnabled', 'validator', 
# 'visibleRegion', 'whatsThis', 'wheelEvent', 'width', 'widthMM', 'winId', 'window', 'windowActivationChange', 'windowFilePath', 
# 'windowFlags', 'windowIcon', 'windowIconText', 'windowModality', 'windowOpacity', 'windowRole', 'windowState', 'windowTitle', 
# 'windowType', 'x', 'x11Info', 'x11PictureHandle', 'y']


## ModelTree

# ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattr__', 
# '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', 
# '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 
# 'beginInsertColumns', 'beginInsertRows', 'beginMoveColumns', 'beginMoveRows', 'beginRemoveColumns', 
# 'beginRemoveRows', 'beginResetModel', 'blockSignals', 'buddy', 'canFetchMore', 'changePersistentIndex', 
# 'changePersistentIndexList', 'childEvent', 'children', 'columnCount', 'columnsAboutToBeInserted', 
# 'columnsAboutToBeMoved', 'columnsAboutToBeRemoved', 'columnsInserted', 'columnsMoved', 'columnsRemoved', 
# 'connect', 'connectNotify', 'createIndex', 'customEvent', 'data', 'dataChanged', 'decodeData', 'deleteLater', 
# 'destroyed', 'disconnect', 'disconnectNotify', 'dropMimeData', 'dumpObjectInfo', 'dumpObjectTree', 
# 'dynamicPropertyNames', 'emit', 'encodeData', 'endInsertColumns', 'endInsertRows', 'endMoveColumns', 
# 'endMoveRows', 'endRemoveColumns', 'endRemoveRows', 'endResetModel', 'event', 'eventFilter', 'fetchMore', 
# 'findChild', 'findChildren', 'flags', 'hasChildren', 'hasIndex', 'headerData', 'headerDataChanged', 'index', 
# 'inherits', 'insertColumn', 'insertColumns', 'insertRow', 'insertRows', 'installEventFilter', 'isWidgetType', 
# 'itemData', 'killTimer', 'layoutAboutToBeChanged', 'layoutChanged', 'match', 'metaObject', 'mimeData', 
# 'mimeTypes', 'modelAboutToBeReset', 'modelReset', 'moveToThread', 'objectName', 'parent', 
# 'persistentIndexList', 'property', 'pyqtConfigure', 'receivers', 'removeColumn', 'removeColumns', 
# 'removeEventFilter', 'removeRow', 'removeRows', 'reset', 'resetInternalData', 'revert', 'roleNames', 
# 'rootItem', 'rowCount', 'rowsAboutToBeInserted', 'rowsAboutToBeMoved', 'rowsAboutToBeRemoved', 'rowsInserted', 
# 'rowsMoved', 'rowsRemoved', 'sender', 'senderSignalIndex', 'setData', 'setHeaderData', 'setItemData', 
# 'setObjectName', 'setParent', 'setProperty', 'setRoleNames', 'setSupportedDragActions', 'setupModelData', 
# 'sibling', 'signalsBlocked', 'sort', 'span', 'startTimer', 'staticMetaObject', 'submit', 
# 'supportedDragActions', 'supportedDropActions', 'thread', 'timerEvent', 'tr', 'trUtf8']
