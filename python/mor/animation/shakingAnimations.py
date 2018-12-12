# -*- coding: utf-8 -*-
from math import cos
from math import sin

def upDateValue(actualValue,actuatorMaxPull,actuatorIncrement):
    if actualValue < actuatorMaxPull:
        print "INCREMENT ++"
        return actualValue + actuatorIncrement
    else:
        print "Done"
        return actualValue

def rotationPoint(Pos0, angle, brasLevier):
    size0 = len(Pos0);
    posOut = [0.0]*3*size0;

    for i in range(size0):
        posOut[3*i] = Pos0[i][0]- brasLevier*cos(angle);
        posOut[3*i+1] = Pos0[i][1] - brasLevier*sin(angle);
        posOut[3*i+2] = Pos0[i][2]
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

            actualValue = objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value[0][0]
            actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
            objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value = actualValue

            print ("Updated Value :"+str(actualValue)+'\n')

def shakingSofia( objToAnimate, dt, factor, **param):
    """
    **Animation function made specifically to shake the leg of 
    the** `6-legged Robot <https://modelorderreduction.readthedocs.io/en/latest/usage/examples/Sofia/sofia.html>`_
    
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
        print("For Actuator : "+objToAnimate.location)
        actualValue = objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value

        objToAnimate.params['angle'] = upDateValue( objToAnimate.params['angle'],
                                                    objToAnimate.params['rangeOfAction'],
                                                    objToAnimate.params['incr'])

        newPos = rotationPoint(actualValue, -objToAnimate.params['angle'], objToAnimate.params['rodRadius'])
        objToAnimate.item.findData(objToAnimate.params["dataToWorkOn"]).value = newPos

        print ("Updated Value :"+str(actualValue)+'\n')

def shakingInverse( objToAnimate, dt, factor, **param):
    """
    **TODO**
    """
    moduloResult = int( round( (factor * objToAnimate.duration)*1000 ) ) % int(  dt * objToAnimate.params['incrPeriod']*1000  )
    # print("currentTime - startTime : "+str(factor * objToAnimate.duration))
    if moduloResult == 0:
        print("For Actuator : "+objToAnimate.location)

        actualValue = objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]]
        actualValue = upDateValue(actualValue,objToAnimate.params['rangeOfAction'],objToAnimate.params['incr'])
        objToAnimate.obj.findData(objToAnimate.params["dataToWorkOn"]).value[objToAnimate.params["goalNbr"]] = actualValue

        print ("Updated Value :"+str(actualValue)+'\n')
