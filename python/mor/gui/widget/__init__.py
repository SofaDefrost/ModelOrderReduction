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

from mor.gui.widget.frameLayout import FrameLayout
from mor.gui.widget.completer import Completer
from mor.gui.widget.treeModel import TreeModel
from mor.gui.widget.genericDialogForm import GenericDialogForm