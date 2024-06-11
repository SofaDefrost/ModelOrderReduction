#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Sofa

class waveController(Sofa.PythonScriptController):

    def initGraph(self, node):
            
            self.rearLeftCavityNode = node.getChild('rearLeftCavity')   # 1
            self.rearRightCavityNode = node.getChild('rearRightCavity') # 2
            self.frontLeftCavityNode = node.getChild('frontLeftCavity') # 3
            self.frontRightCavityNode = node.getChild('frontRightCavity') # 4
            self.centerCavityNode = node.getChild('centerCavity') # 0
            
            self.controlledItem = 0
            self.inflation = True
            self.time = 0.0
            
    def onBeginAnimationStep(self,dt):
            increment = 250
            self.time = self.time + dt
            
                
            if (self.inflation == True):
                pressureValue = 0
                if (self.controlledItem == 1):
                    pressureValue = self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 3500):
                        self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    else:
                        self.controlledItem = 2
                if (self.controlledItem == 0):
                    pressureValue = self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                if (self.controlledItem == 0):
                    pressureValue = self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    else:
                        self.controlledItem = 1
                if (self.controlledItem == 2):
                    pressureValue = self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                if (self.controlledItem == 2):
                    pressureValue = self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    else:
                        self.controlledItem = 0
                        self.inflation = False
                    
            else:
                
                    if (self.controlledItem == 1):
                        pressureValue = self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                        if (pressureValue >= 0):
                            self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                        else:
                            self.controlledItem = 2
                    if (self.controlledItem == 0):
                        pressureValue = self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                        if (pressureValue >= 0):
                            self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    if (self.controlledItem == 0):
                        pressureValue = self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                        if (pressureValue >= 0):
                            self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                        else:
                            self.controlledItem = 1
                    if (self.controlledItem == 2):
                        pressureValue = self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                        if (pressureValue >= 0):
                            self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    if (self.controlledItem == 2):
                        pressureValue = self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                        if (pressureValue >= 0):
                            self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                        else:
                            self.controlledItem = 0
                            self.inflation = True


