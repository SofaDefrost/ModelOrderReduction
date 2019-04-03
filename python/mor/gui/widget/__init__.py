# -*- coding: utf-8 -*-
"""
**Set of custom Widget used to created the MOR GUI**

**Content:**

.. autosummary::
    :toctree: _autosummary

    mor.gui.widget.completer
    mor.gui.widget.frameLayout
    mor.gui.widget.genericDialogForm
    mor.gui.widget.treeModel

"""
__all__=["completer","frameLayout","genericDialogForm","treeModel"]

from frameLayout import FrameLayout
from completer import Completer
from treeModel import TreeModel
from genericDialogForm import GenericDialogForm