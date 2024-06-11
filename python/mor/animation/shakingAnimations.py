# -*- coding: utf-8 -*-
"""
Implemented animation functions
"""
from math import cos
from math import sin

def upDateValue(actualValue,actuatorMaxPull,actuatorIncrement):
    """
    Utility function for default animation.

    Increment a sofa data value until fixed amount

    :param actualValue:
    :param actuatorMaxPull:
    :param actuatorIncrement:
    :return: actualValue :
    """
    if actualValue < actuatorMaxPull:
        print ("INCREMENT ++")
        return actualValue + actuatorIncrement
    else:
        print ("Done")
        return actualValue

def rotationPoint(Pos0, angle, brasLevier):
    """
    Utility function applying rotation on a given position with some lever arm

    :param Pos0:
    :param angle:
    :param brasLevier:
    :return: New updated position
    """
    print ("In rotation POint")
    size0 = len(Pos0);
    posOut = []

    for i in range(size0):
        posOut.append([Pos0[i][0]- brasLevier*cos(angle),
                       Pos0[i][1] - brasLevier*sin(angle),
                       Pos0[i][2]])

    print(posOut)
    return posOut

lastTime = 0
def defaultShaking( objToAnimate, dt, factor, **param):
    """
    **Default animation function** 

    The animation consist on *increasing* a value of a Sofa object until it reach its *maximum*

    To use it the **params** parameters of :py:class:`.ObjToAnimate` which is a dictionnary will need 4 keys:

    **Keys:**

    +---------------+-------+---------------------------------------------------------------------------------+
    | argument      | type  | definition                                                                      |
    +===============+=======+=================================================================================+
    | dataToWorkOn  | str   | Name of the Sofa datafield we will work on by default it will be set to *value* |
    +---------------+-------+---------------------------------------------------------------------------------+
    | incrPeriod    | float | Period between each increment                                                   |
    +---------------+-------+---------------------------------------------------------------------------------+
    | incr          | float | Value of each increment                                                         |
    +---------------+-------+---------------------------------------------------------------------------------+
    | rangeOfAction | float | Until which value the data will increase                                        |
    +---------------+-------+---------------------------------------------------------------------------------+

    :return: None
    """
    import Sofa
    global lastTime
    writeCurrent = False
    time = factor * objToAnimate.duration
    period = dt * objToAnimate.params['incrPeriod']

    argList = ['dataToWorkOn','incrPeriod','incr','rangeOfAction']
    
    if not all(objToAnimate.params["dataToWorkOn"]):
        
        raise('Missing parameter')

    else:

        if (time == dt):
            writeCurrent = True

        if (time-(lastTime + period + dt) >= 0.000001): # (time > (lastTime + period + dt)):
            lastTime += period

        if ( abs(time-(lastTime + period + dt)) <= 0.000001 ):
            writeCurrent = True

        if (writeCurrent):
            print("For Actuator : "+objToAnimate.location)
            actualValue = objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value[0]#[0]
            actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
            objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value = [float(actualValue)]

            print ("Updated Value :"+str(actualValue)+'\n')

def doingCircle( objToAnimate, dt, factor, **param):
    """
    **Animation function made specifically to apply deformation on the liver scene.**
    
    It's an example of what can be a custom shaking animation.
    The animation consist on taking a position in entry, rotate it, and then update it in the component.

    To use it the **params** parameters of :py:class:`.ObjToAnimate` which is a dictionnary will need 6 keys:

    **Keys:**

    +---------------+-------+-----------------------------------------------------------------------+
    | argument      | type  | definition                                                            |
    +===============+=======+=======================================================================+
    | dataToWorkOn  | str   | Name of the Sofa datafield we will work on here it will be *position* |
    +---------------+-------+-----------------------------------------------------------------------+
    | incrPeriod    | float | Period between each increment                                         |
    +---------------+-------+-----------------------------------------------------------------------+
    | incr          | float | Value of each increment                                               |
    +---------------+-------+-----------------------------------------------------------------------+
    | rangeOfAction | float | Until which value the data will increase                              |
    +---------------+-------+-----------------------------------------------------------------------+
    | angle         | float | Initial angle value in radian                                         |
    +---------------+-------+-----------------------------------------------------------------------+
    | rodRadius     | float | Radius Lenght of the circle                                           |
    +---------------+-------+-----------------------------------------------------------------------+
    """
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        currentPositions = objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value

        objToAnimate.params['angle'] = upDateValue( objToAnimate.params['angle'],
                                                    objToAnimate.params['rangeOfAction'],
                                                    objToAnimate.params['incr'])
        
        with objToAnimate.item.position.writeable() as positions:
            newPositions = rotationPoint(positions, -objToAnimate.params['angle'], objToAnimate.params['rodRadius'])
            for i in range(len(positions)):
                positions[i] = newPositions[i]            


def shakingInverse( objToAnimate, dt, factor, **param):
    """
    **Animation function to use with iinverse simulation**

    """
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)

        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]]
        actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]] = actualValue

        print ("Updated Value :"+str(actualValue)+'\n')

def doingNothing( objToAnimate, dt, factor, **param):
    """
    **Default animation function** 

    The animation consist on *increasing* a value of a Sofa object until it reach its *maximum*

    To use it the **params** parameters of :py:class:`.ObjToAnimate` which is a dictionnary will need 4 keys:

    **Keys:**

    +---------------+-------+---------------------------------------------------------------------------------+
    | argument      | type  | definition                                                                      |
    +===============+=======+=================================================================================+
    | dataToWorkOn  | str   | Name of the Sofa datafield we will work on by default it will be set to *value* |
    +---------------+-------+---------------------------------------------------------------------------------+
    | incrPeriod    | float | Period between each increment                                                   |
    +---------------+-------+---------------------------------------------------------------------------------+
    | incr          | float | Value of each increment                                                         |
    +---------------+-------+---------------------------------------------------------------------------------+
    | rangeOfAction | float | Until which value the data will increase                                        |
    +---------------+-------+---------------------------------------------------------------------------------+

    :return: None
    """
    global lastTime
    writeCurrent = False
    time = factor * objToAnimate.duration
    period = dt * objToAnimate.params['incrPeriod']

    if (time == dt):
        writeCurrent = True

    if (time-(lastTime + period + dt) >= 0.000001): # (time > (lastTime + period + dt)):
        lastTime += period

    if ( abs(time-(lastTime + period + dt)) <= 0.000001 ):
        writeCurrent = True

    if (writeCurrent):
        print ("Doing Nothing")
