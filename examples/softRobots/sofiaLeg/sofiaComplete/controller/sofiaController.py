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

class SofiaController(Sofa.PythonScriptController):

    def initGraph(self, node):

        self.node = node
        print self.node.name
        self.name = "SofiaControlManager"

    def init(self,actuators,auto=True):

        self.auto = auto
        self.actuators = actuators


    def onKeyPressed(self,c):

        if (c == chr(18)):
            self.actuators[0].setDirectionBackward()
            self.actuators[2].setDirectionBackward()
            self.actuators[5].setDirectionBackward()

            self.actuators[1].setDirectionForward()
            self.actuators[3].setDirectionForward()
            self.actuators[4].setDirectionForward()
            print("--------------- >    Left")

        if (c == chr(20)):
            self.actuators[0].setDirectionForward()
            self.actuators[2].setDirectionForward()
            self.actuators[5].setDirectionForward()
            
            self.actuators[1].setDirectionBackward()
            self.actuators[3].setDirectionBackward()
            self.actuators[4].setDirectionBackward()
            print("--------------- >    Right")

        if (c == chr(19)):
            self.actuators[0].setDirectionForward()
            self.actuators[2].setDirectionForward()
            self.actuators[5].setDirectionForward()
            
            self.actuators[1].setDirectionForward()
            self.actuators[3].setDirectionForward()
            self.actuators[4].setDirectionForward()
            print("--------------- >    Forward")
        if (c == chr(21)):
            self.actuators[0].setDirectionBackward()
            self.actuators[2].setDirectionBackward()
            self.actuators[5].setDirectionBackward()
            
            self.actuators[1].setDirectionBackward()
            self.actuators[3].setDirectionBackward()
            self.actuators[4].setDirectionBackward()
            print("--------------- >    Backward")