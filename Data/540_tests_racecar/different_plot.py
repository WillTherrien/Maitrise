'''

Written by William Therrien, August 2020

'''

import rosbag, sys, csv
import time
import tf
import string
import os #for file management make directory
import numpy as np
import matplotlib.pyplot as plt


#verify correct input arguments: 1 or 2
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

count = 0
X_list_v = []
Y_list_v = []
X_list_l = []
Y_list_l = []
bagNumber_list = []

for bagFile in listOfBagFiles:
	count += 1
	print "reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile
	#access bag
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename
	bagNumber = ''.join([n for n in bagName if n.isdigit()])

	#get list of topics from the bag
	encd_pos = []
	t_encd = []
	X_vic = []
	Y_vic = []
	theta_vic = []
	t_vic = []
	X_las = []
	Y_las = []
	theta_las = []
	t_las = []
	X_v_real = []
	Y_v_real = []
	theta_v_real = []
	X_l_real = []
	Y_l_real = []
	theta_l_real = []
	k_encd = 0
	trigger = 1
	trigger_vic = 1
	trigger_las = 1

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
		if (topic == "/pose_stamped"):
			X_las.append(msg.pose.position.x)
			Y_las.append(msg.pose.position.y)
			quat_las = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
			theta_las.append(tf.transformations.euler_from_quaternion(quat_las)[2])
			t_las.append(t)


	# INTERPOLATION POUR LE TEMPS ROS DU TRIGGER
	for i in range(len(encd_pos)):
		if (encd_pos[i] > 4.0 and trigger == 1):
			t_encd_over = t_encd[i]
			encd_pos_over  = encd_pos[i]
			k_encd = i-1
			trigger = 0
	t_encd_under = t_encd[k_encd]
	encd_pos_under = encd_pos[k_encd]
	time_trigger = t_encd_under+(4.0-encd_pos_under)*(t_encd_over-t_encd_under)/(encd_pos_over-encd_pos_under)

	# INTERPOLATION POUR LA POSITION INITIALE DU VICON
	for i in range(len(X_vic)):
		if (t_vic[i]>time_trigger and trigger_vic ==1):
			t_vic_over = t_vic[i]
			X_vic_over = X_vic[i]
			Y_vic_over = Y_vic[i]
			theta_vic_over = theta_vic[i]
			k_vic = i-1
			trigger_vic = 0
	t_vic_under = t_vic[k_vic]
	X_vic_under = X_vic[k_vic]
	Y_vic_under = Y_vic[k_vic]
	theta_vic_under = theta_vic[k_vic]

	X_vic_ini = X_vic_under+(time_trigger-t_vic_under)*(X_vic_over-X_vic_under)/(t_vic_over-t_vic_under)
	Y_vic_ini = Y_vic_under+(time_trigger-t_vic_under)*(Y_vic_over-Y_vic_under)/(t_vic_over-t_vic_under)
	theta_vic_ini = theta_vic_under+(time_trigger-t_vic_under)*(theta_vic_over-theta_vic_under)/(t_vic_over-t_vic_under)

	# CREATION DU VECTEUR DE POSITION VICON PENDANT MANOEUVRE
	X_v_real.append(0)
	Y_v_real.append(0)
	theta_v_real.append(0)
	for i in range(len(X_vic)):
		if (X_vic[i]>X_vic_ini):
			#X_v_real.append(X_vic[i]-X_vic_ini)
			#Y_v_real.append(Y_vic[i]-Y_vic_ini)
			#theta_v_real.append(theta_vic[i]-theta_vic_ini)
			X_v_real.append((X_vic[i]-X_vic_ini)*np.cos(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.sin(theta_vic_ini))
			Y_v_real.append(-(X_vic[i]-X_vic_ini)*np.sin(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.cos(theta_vic_ini))
			theta_v_real.append(theta_vic[i]-theta_vic_ini)
			
	X_list_v.append(X_v_real)
	Y_list_v.append(Y_v_real)

	# INTERPOLATION POUR LA POSITION INITIALE DU LASER_SCAN_MATCHER
	for i in range(len(X_las)):
		if (t_las[i]>time_trigger and trigger_las ==1):
			t_las_over = t_las[i]
			X_las_over = X_las[i]
			Y_las_over = Y_las[i]
			theta_las_over = theta_las[i]
			k_las = i-1
			trigger_las = 0
	t_las_under = t_las[k_las]
	X_las_under = X_las[k_las]
	Y_las_under = Y_las[k_las]
	theta_las_under = theta_las[k_las]

	X_las_ini = X_las_under+(time_trigger-t_las_under)*(X_las_over-X_las_under)/(t_las_over-t_las_under)
	Y_las_ini = Y_las_under+(time_trigger-t_las_under)*(Y_las_over-Y_las_under)/(t_las_over-t_las_under)
	theta_las_ini = theta_las_under+(time_trigger-t_las_under)*(theta_las_over-theta_las_under)/(t_las_over-t_las_under)

	# CREATION DU VECTEUR DE POSITION VICON PENDANT MANOEUVRE
	X_l_real.append(0)
	Y_l_real.append(0)
	theta_l_real.append(0)
	for i in range(len(X_las)):
		if (X_las[i]>X_las_ini):

			X_l_real.append((X_las[i]-X_las_ini)*np.cos(theta_las_ini)+(Y_las[i]-Y_las_ini)*np.sin(theta_las_ini))
			Y_l_real.append(-(X_las[i]-X_las_ini)*np.sin(theta_las_ini)+(Y_las[i]-Y_las_ini)*np.cos(theta_las_ini))
			theta_l_real.append(theta_las[i]-theta_las_ini)

	X_list_l.append(X_l_real)
	Y_list_l.append(Y_l_real)
	bagNumber_list.append(bagNumber)

	bag.close()

for i in range(len(X_list_v)):
	plt.figure(i)
	plt.axis("equal")
	plt.plot(X_list_v[i],Y_list_v[i],'-b', label='Position vicon')
	plt.plot(X_list_l[i],Y_list_l[i],'-r', label='Position laser')
	plt.title(bagNumber_list[i])
	plt.xlabel('X_position (m)')
	plt.ylabel('Y_position (m)')
	plt.legend()


plt.show()

print "Done reading all " + numberOfFiles + " bag files."



