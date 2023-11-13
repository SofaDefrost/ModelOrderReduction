# -*- coding: utf-8 -*-

class ObjToAnimate():
    '''
    **Class allowing us to store in 1 object all the information about a specific animation**

    **Args**

    +------------+-----------+---------------------------------------------------------------------------------------+
    | argument   | type      | definition                                                                            |
    +============+===========+=======================================================================================+
    | location   | Str       | Path to obj/node we want to animate                                                   |
    +------------+-----------+---------------------------------------------------------------------------------------+
    | animFct    | Str       |  Name of our function we want to use to animate.                                      |
    |            |           |  During execution of the Sofa Scene, it will import the module                        |
    |            |           |  mor.animation.animFct where your function has to be located in order to be used.     |
    +------------+-----------+---------------------------------------------------------------------------------------+
    | item       | Sofa.Node | pointer to Sofa node/obj                                                              |
    |            | Sofa.Obj  | in which we are working on (will be set during execution).                            |
    +------------+-----------+---------------------------------------------------------------------------------------+
    | duration   | seconde   |  Total time in second of the animation \(put by default to -1                         |
    |            |(in float) |  \& will be calculated & set later during the execution)                              |
    +------------+-----------+---------------------------------------------------------------------------------------+
    | \*\*params | undefined |  You can put in addition whatever parameters you will need                            |
    |            |           |  for your specific animation function, they will be passed                            |
    |            |           |  to the *animFct* you have chosen during execution                                    |
    |            |           |  See :mod:`mor.animation` for the specific parameters                                 |
    |            |           |  you need to give to each animation function                                          |
    +------------+-----------+---------------------------------------------------------------------------------------+

    **Example**

        To use the animation :py:func:`.defaultShaking` this is how you declare your :py:class:`.ObjToAnimate`:

        .. sourcecode:: python

            ObjToAnimate( "myNodeToReduce/myComponentToAnimate",
                          "defaultShaking",
                          incr= 5, incrPeriod= 10, rangeOfAction= 40,
                          dataToWorkOn= NameOfDataFieldsToWorkOn)

        *or for default behavior*
        
        .. sourcecode:: python

            ObjToAnimate( "myNodeToReduce/myComponentToAnimate",
                          incr=5,incrPeriod=10,rangeOfAction=40)

    '''

    def __init__(self,location, animFct='defaultShaking', item=None, duration=-1, **params):
        self.location = location # #: location var
        self.animFct = animFct
        self.item = item
        self.duration = duration
        self.params = params 
        # name, dataToWorkOn, incr, incrPeriod, rangeOfAction ...
