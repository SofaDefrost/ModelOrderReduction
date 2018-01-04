#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Sofa
import os
import math
import numpy as np
import yaml

################################################################################################
## Init variables from data in yaml config file

#Load config file
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

connectivityFileName =  cfg['connectivityFileName']
pathFile = 				cfg['weightsAndRID']['pathTodir']

################################################################################################


class saveNodesInfo(Sofa.PythonScriptController):

    def initGraph(self, node):
        
        self.node = node

        tetrahedra = self.node.getObject('loader').findData("tetrahedra").value
        np.savetxt(pathFile+connectivityFileName, tetrahedra,fmt='%i')
        print "Saved tetrahedra in", pathFile+connectivityFileName