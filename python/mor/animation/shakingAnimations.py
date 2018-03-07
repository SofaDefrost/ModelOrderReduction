# -*- coding: utf-8 -*-
import Sofa

"""
Files containing all the developped shaking animation 
function to help produced a reduced model

"""
def upDateValue(phaseTest,actualValue,actuatorMaxPull,actuatorIncrement):

	if phaseTest == 1:
		if actualValue < actuatorMaxPull:
			print "INCREMENT ++"
			return actualValue + actuatorIncrement
		else:
			print "Done"
			return actualValue
	else:
		if actualValue >= actuatorIncrement:
			print "INCREMENT --"
			return actualValue - actuatorIncrement
		else:
			print "Done"
			return actualValue

def defaultShaking( target,
					phaseTest,
					actuatorNb,
					actuatorMaxPull,
					actuatorBreathTime,
					actuatorIncrement,
					breathTimeCounter):
	"""
	Object with an elastic deformation law.

	Args:
	    target (Sofa.node): 	Sofa node in wich we are working

	    phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

	    actuatorNb (int):   	The number of our actuator we are currently working with

	"""
	if actuatorBreathTime == breathTimeCounter.tmp[actuatorNb]:
		print("For Actuator : "+str(target.name))
		actualValue = None
		myObjName = None
		for obj in target.getObjects():
			if obj.getClassName() ==  'CableConstraint':
				myObjName = obj.name
			elif obj.getClassName() ==  'SurfacePressureConstraint':
				myObjName = obj.name

		if myObjName:
			actualValue = target.getObject(myObjName).findData('value').value[0][0]

			# print (	"with actualValue :", 	actualValue,
			# 		"a maxPull of :", 		actuatorMaxPull,
			# 		"& INCREMENT :", 		actuatorIncrement)

			actualValue = upDateValue(phaseTest[actuatorNb],actualValue,actuatorMaxPull,actuatorIncrement)

			print ("Updated Value :"+str(actualValue)+'\n')

			target.getObject(myObjName).findData('value').value = actualValue
		else:
			print 'Err'	

		breathTimeCounter.tmp[actuatorNb] = 0

	else:
		breathTimeCounter.tmp[actuatorNb] += 1