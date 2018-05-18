# -*- coding: utf-8 -*-
from math import cos
from math import sin
"""
Files containing all the developped shaking animation 
function to help produced a reduced model



"""
def upDateValue(actualValue,actuatorMaxPull,actuatorIncrement):
    if actualValue < actuatorMaxPull:
        print "INCREMENT ++"
        return actualValue + actuatorIncrement
    else:
        print "Done"
        return actualValue

def defaultShaking( objToAnimate,
                    dt,
                    factor,
                    **param):
    """
    Object with an elastic deformation law.

    Args:
        target (Sofa.node): 	Sofa node in wich we are working

        phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

        actuatorNb (int):   	The number of our actuator we are currently working with

    """
    import Sofa
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)

        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[0][0]
        actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value = actualValue

        print ("Updated Value :"+str(actualValue)+'\n')

def shakingSofia( objToAnimate,
                  dt,
                  factor,
                  **param):
    """
    shakingSofia

    Args:
        target (Sofa.node):     Sofa node in wich we are working

        phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

        actuatorNb (int):       The number of our actuator we are currently working with
    """

    global angle

    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)
        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value

        objToAnimate.params['angle'] = upDateValue( objToAnimate.params['angle'],
                                                    objToAnimate.params['rangeOfAction'],
                                                    objToAnimate.params['incr'])

        newPos = rotationPoint(actualValue, -objToAnimate.params['angle'], objToAnimate.params['rodRadius'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value = newPos

        print ("Updated Value :"+str(actualValue)+'\n')


def rotationPoint(Pos0, angle, brasLevier):
    size0 = len(Pos0);
    posOut = [0.0]*3*size0;

    for i in range(size0):
        posOut[3*i] = Pos0[i][0] - brasLevier*cos(angle);
        posOut[3*i+1] = Pos0[i][1] - brasLevier*sin(angle);
        posOut[3*i+2] = Pos0[i][2];
        print(posOut)

    return posOut

def shakingInverse( objToAnimate,
                    dt,
                    factor,
                    **param):
    """
    shakingInverse

    Args:
        target (Sofa.node):     Sofa node in wich we are working

        phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

        actuatorNb (int):       The number of our actuator we are currently working with
    """
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)

        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]]
        actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]] = actualValue

        print ("Updated Value :"+str(actualValue)+'\n')
