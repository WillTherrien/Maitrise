'''

Written by William Therrien, August 2020

'''

import rosbag, sys, csv
import time
import tf
import os #for file management make directory
import numpy as np
import matplotlib.pyplot as plt



#Get list of bags in current folder
if (len(sys.argv) > 2):
	print "invalid number of arguments:   " + str(len(sys.argv))
	print "should be 2: 'bag2csv.py' and 'bagName'"
	print "or just 1  : 'bag2csv.py'"
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfBagFiles = [sys.argv[1]]
	numberOfFiles = "1"
	print "reading only 1 bagfile: " + str(listOfBagFiles[0])
elif (len(sys.argv) == 1):
	listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfBagFiles))
	print "reading all " + numberOfFiles + " bagfiles in current directory: \n"
	for f in listOfBagFiles:
		print f

else:
	print "bad argument(s): " + str(sys.argv)	#shouldnt really come up
	sys.exit(1)

#Init
count = 0
X_list_v = []
Y_list_v = []
bagNumber_list = []

# Read each bag individually 
for bagFile in listOfBagFiles:
	
	count += 1
	print "reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile
	
	#Get bag number
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename
	bagNumber = ''.join([n for n in bagName if n.isdigit()])

	#Init
	encd_pos = []
	t_encd = []
	X_vic = []
	Y_vic = []
	theta_vic = []
	t_vic = []
	X_v_real = []
	Y_v_real = []
	theta_v_real = []
	k_encd = 0
	trigger = 1
	trigger_vic = 1

	#Access topics
	for topic, msg, t in bagContents:

		if (topic == "/prop_sensors"):
			encd_pos.append(msg.data[0])
			t_encd.append(t)
		if (topic == "/states"):
			X_vic.append(msg.pose.position.x)
			Y_vic.append(msg.pose.position.y)
			quat_vic = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
			theta_vic.append(tf.transformations.euler_from_quaternion(quat_vic)[2])
			t_vic.append(t)

	# FIND TIME AT WHICH THE MANOEUVRE STARTS
	for i in range(len(encd_pos)):
		if (encd_pos[i] > 4.0 and trigger == 1):
			time_trigger = t_encd[i]
			trigger = 0

			
	# SET INITIAL POSITION OF THE VEHICULE AT THAT TIME
	for i in range(len(X_vic)):
		if (t_vic[i]>time_trigger and trigger_vic ==1):
			k_vic = i
			trigger_vic = 0


	X_vic_ini = X_vic[k_vic]
	Y_vic_ini = Y_vic[k_vic]
	theta_vic_ini = theta_vic[k_vic]

	# CREATION DU VECTEUR DE POSITION VICON PENDANT MANOEUVRE
	X_v_real.append(0)
	Y_v_real.append(0)
	theta_v_real.append(0)
	for i in range(len(X_vic)):
		if (X_vic[i]>X_vic_ini):
			X_v_real.append((X_vic[i]-X_vic_ini)*np.cos(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.sin(theta_vic_ini))
			Y_v_real.append(-(X_vic[i]-X_vic_ini)*np.sin(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.cos(theta_vic_ini))
			theta_v_real.append(theta_vic[i]-theta_vic_ini)
			
	X_list_v.append(X_v_real)
	Y_list_v.append(Y_v_real)

	bagNumber_list.append(bagNumber)
		

	bag.close()

plt.figure(1)
for i in range(len(X_list_v)):

	plt.plot(X_list_v[i],Y_list_v[i],'-b', label='Position vicon')
	plt.title("All paths")
	plt.xlabel('X_position (m)')
	plt.ylabel('Y_position (m)')
	plt.axis("equal")
	#plt.legend()


plt.show()

print "Done reading all " + numberOfFiles + " bag files."



