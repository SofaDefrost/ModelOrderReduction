# -*- coding: utf-8 -*-

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
    import Sofa
    """
    Object with an elastic deformation law.

    Args:
        target (Sofa.node): 	Sofa node in wich we are working

        phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

        actuatorNb (int):   	The number of our actuator we are currently working with

    """
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)

        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[0][0]
        actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value = actualValue

        print ("Updated Value :"+str(actualValue)+'\n')