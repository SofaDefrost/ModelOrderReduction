#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Sofa

class keyInteractiveController(Sofa.PythonScriptController):

    def initGraph(self, node):
            
            self.rearLeftCavityNode = node.getChild('rearLeftCavity')   # 1
            self.rearRightCavityNode = node.getChild('rearRightCavity') # 2
            self.frontLeftCavityNode = node.getChild('frontLeftCavity') # 3
            self.frontRightCavityNode = node.getChild('frontRightCavity') # 4
            self.centerCavityNode = node.getChild('centerCavity') # 0
            self.controlledItem = 0

    def onKeyPressed(self,c):
            increment = 100
            print 'c is: ', c
            if (c == "0"):
                self.controlledItem = 0
            elif (c == "1"):
                self.controlledItem = 1
            elif (c == "2"):
                self.controlledItem = 2
            elif (c == "3"):
                self.controlledItem = 3
            elif (c == "4"):
                self.controlledItem = 4
            
            if (c == "+"):
                pressureValue = 0
                if (self.controlledItem == 0):
                    pressureValue = self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 3500):
                        self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 1):
                    pressureValue = self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 2):
                    pressureValue = self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 3):
                    pressureValue = self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                else:
                    pressureValue = self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] + increment
                    if (pressureValue <= 2000):
                        self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                    

            if (c == "-"):
                if (self.controlledItem == 0):
                    pressureValue = self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                    if (pressureValue >= 0):
                        self.centerCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 1):
                    pressureValue = self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                    if (pressureValue >= 0):
                        self.rearLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 2):
                    pressureValue = self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                    if (pressureValue >= 0):
                        self.rearRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                elif (self.controlledItem == 3):
                    pressureValue = self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                    if (pressureValue >= 0):
                        self.frontLeftCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)
                else:
                    pressureValue = self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value[0][0] - increment
                    if (pressureValue >= 0):
                        self.frontRightCavityNode.getObject('SurfacePressureConstraint').findData('value').value = str(pressureValue)


