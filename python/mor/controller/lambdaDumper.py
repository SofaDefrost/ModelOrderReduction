#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Sofa

class storeLambda(Sofa.PythonScriptController):

    def onLoaded(self,node):
        
            print('############## Python example: variables ##############')
            print('### This example scene demonstrates how to pass string variables from a SOFA scn to the python script')
            print('### Note that the variables can be modified in the SOFA GUI')
            print('##########################################################')
            
            self.lambdaValuesFile = self.findData('variables').value[0][0]
            
            print('At initialization, variables = ', self.lambdaValuesFile)
                                
            return 0


    def initGraph(self, node):
            self.node = node
            with open(self.lambdaValuesFile, "w") as myfile:
                myfile.write("")

    def onEndAnimationStep(self,dt):
            lambdaTab = self.node.getObject('GSSolver').findData('constraintForces')
            print('Contraint forces:', lambdaTab.value, len(lambdaTab.value))
            with open(self.lambdaValuesFile, "a") as myfile:
                for i in lambdaTab.value:                   
                    myfile.write(str(i[0])+ " ")
                myfile.write("\n")
            #displacement = inputvalue.value[0][0] + 0.05
            #inputvalue.value = str(displacement)
            #inputvalue = self.node.getObject('aCableActuator').findData('value')
            
            #if (c == "+"):
               #displacement = inputvalue.value[0][0] + 1.
               #inputvalue.value = str(displacement)
               
            #elif (c == "-"):
               #displacement = inputvalue.value[0][0] - 1.
               #if(displacement < 0):
		  #displacement = 0
               #inputvalue.value = str(displacement)
 




