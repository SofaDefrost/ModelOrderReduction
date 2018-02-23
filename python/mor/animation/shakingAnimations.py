# -*- coding: utf-8 -*-
import Sofa

"""
Files containing all the developped shaking animation 
function to help produced a reduced model

"""
def DefaultShaking( target, 
					phaseTest,
					actuatorNb,
					actuatorMaxPull,
					actuatorBreathTime,
					actuatorIncrement,
					breathTimeCounter, **param):
	"""
	Object with an elastic deformation law.

	Args:
	    target (Sofa.node): 	Filepath to a volumetric mesh (VTK,VTU, GMESH)

	    factor (float):  		...

	    phaseTest (list[int]):  activation of actuator sequence (ie: [1,0,0,1])

	    actuatorNb (int):   	The number of our actuator we are currently working with

	"""
	if actuatorBreathTime == breathTimeCounter.tmp[actuatorNb]:
		actualValue = target.getObject('CableConstraint').findData('value').value[0][0]	
		print(	"For Actuator : ", 		target.name,
				"with actualValue :", 	actualValue,
				"a maxPull of :", 		actuatorMaxPull,
				"& INCREMENT :", 		actuatorIncrement)

		if phaseTest[actuatorNb] == 1:
			if actualValue < actuatorMaxPull:
				print "		INCREMENT ++"
				actualValue = actualValue + actuatorIncrement
			else:
				print "Done for :",target.name
		else:
			if actualValue >= actuatorIncrement:
				print "		INCREMENT --"
				actualValue = actualValue - actuatorIncrement
			else:
				print "Done for :",target.name

		print "Updated Value :",actualValue
		target.getObject('CableConstraint').findData('value').value = actualValue
		breathTimeCounter.tmp[actuatorNb] = 0

	else:
		breathTimeCounter.tmp[actuatorNb] += 1