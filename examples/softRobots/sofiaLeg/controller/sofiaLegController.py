# -*- coding: utf-8 -*-
import Sofa
from math import *

def rotationPoint(Pos0, angle, brasLevier):
    size0 = len(Pos0);
    posOut = [0.0]*3*size0;

    for i in range(size0):
        posOut[3*i] = Pos0[i][0] - brasLevier*cos(angle)
        posOut[3*i+1] = Pos0[i][1] - brasLevier*sin(angle)
        posOut[3*i+2] = Pos0[i][2];

    return posOut

class SofiaLegController(Sofa.PythonScriptController):

    def initGraph(self, node):

        self.node = node
        self.name = "SofiaLegControlManager"
        self.dt = self.node.findData('dt').value
        self.initPos = self.node.getObject('actuatorState').findData('position').value

        # self.auto = 'Not Initialized'

        # self.forward = 'Not Initialized'
        # self.angle = 'Not Initialized'  
        # self.velocity= 'Not Initialized'

        # self.offset = 'Not Initialized'

        # self.leversize = 0.7
        # self.period = 0.02
        # self.incr = 0
        # self.factor = 0

    def init(self,auto=True,forward=True,offset=0):

        self.auto = auto

        self.forward = forward
        if self.forward:
            self.angle=3.14159265359
            self.velocity=0.05
        else:
            self.angle=0
            self.velocity=-0.05

        self.leversize = 0.7
        
        self.period = 0.02

        self.offset = offset
        self.incr = 0

        self.factor = 0
              
    def setDirectionForward(self):
        self.node.getObject('actuatorState').findData('position').value = self.initPos
        self.angle=3.14159265359
        self.velocity=0.05
        self.incr = 0
        print("--------------- >    Forward")

    def setDirectionBackward(self):
        self.node.getObject('actuatorState').findData('position').value = self.initPos
        self.angle=0
        self.velocity=-0.05
        self.incr = 0
        print("--------------- >    Backward")

    def move(self):
        if self.incr == self.offset :
            self.angle = self.angle + self.velocity
            self.pos0 = self.node.getObject('actuatorState').findData('position').value
            newPos = rotationPoint(self.pos0, self.angle, self.leversize)
            self.node.getObject('actuatorState').findData('position').value = newPos
        else:
            self.incr += 1

    def onBeginAnimationStep(self,dt):
        if self.auto:
            self.factor +=1
            moduloResult = int( round( (self.factor * self.dt)*1000 ) ) % int( self.period*1000  )
            if moduloResult == 0:
                self.move()

    def onKeyPressed(self,c):

        if (c == "+"):
            self.setDirectionForward()

        if (c == "-"):
            self.setDirectionBackward()

        if (c == ' '):
            self.move()
