#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import os
import math
import numpy as np

nameFile = "test.txt"
pathFile = os.path.dirname(os.path.abspath(__file__))+"/../ECSWdata_stored/"+nameFile

class saveNodesInfo(Sofa.PythonScriptController):

    def initGraph(self, node):
        
        self.node = node

        tetrahedra = self.node.getObject('loader').findData("tetrahedra").value
        np.savetxt(pathFile, tetrahedra,fmt='%i')
        print "Saved tetrahedra in", pathFile