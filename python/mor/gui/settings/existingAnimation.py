from collections import OrderedDict

'''
File in which you can easily add animation function that you want to be able to select in the GUI

To do that we declare an `OrderedDict` in which we will append the animation we want.
We give as dictionnary entry the name of the animation function and as value another 
dictionnary containing its arguments name with their default values.

example:

existingAnimation['MyNewAnimationFunc'] = { 'incr':5.,
                                        'incrPeriod':10.,
                                        'rangeOfAction':40.,
                                        'additionalArg1':'can be a string',
                                        'additionalArg2':42
                                        ... 
                                        }
'''


existingAnimation = OrderedDict()

existingAnimation['defaultShaking'] = { 'incr':5.,
                                        'incrPeriod':10.,
                                        'rangeOfAction':40.}

existingAnimation['doingCircle'] = { 'incr':0.05,
                                      'incrPeriod':3,
                                      'rangeOfAction':6.4,
                                      'dataToWorkOn':'position',
                                      'angle':0,
                                      'rodRadius':0.7}

existingAnimation['defaultTest'] = { 'incr':5.,
                                        'incrPeriod':10.,
                                        'rangeOfAction':40.}

existingAnimation['doingNothing'] = {'incr':5.,
                                'incrPeriod':10.,
                                'rangeOfAction':40.}