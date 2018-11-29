# -*- coding: utf-8 -*-
"""
**Set of class/function used to created the MOR GUI**

**Content:**

.. autosummary::
    :toctree: _autosummary

    mor.gui.completer
    mor.gui.frameLayout
    mor.gui.genericDialogForm
    mor.gui.treeModel
    mor.gui.utility

"""
__all__=["completer","frameLayout","genericDialogForm","treeModel","utility"]

from frameLayout import FrameLayout
from completer import MyCompleter
from treeModel import TreeModel
from genericDialogForm import GenericDialogForm
