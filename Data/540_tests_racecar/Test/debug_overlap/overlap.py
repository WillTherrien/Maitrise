'''

Written by William Therrien, August 2020

'''

import rosbag, sys, csv
import time
import tf
import string
import os #for file management make directory
import numpy as np
import xlrd
import xlwt
from xlwt import Workbook
from xlutils.copy import copy
import random
import matplotlib.pyplot as plt

# Open workbook
workbook = xlrd.open_workbook('/home/ubuntu/Desktop/racecar_tests.xlsx')
# Choose sheet
xl_sheet = workbook.sheet_by_index(0)
# Read particular columns of a sheet
col_vi = xl_sheet.col(0) #Attribut la colone 1 a la vitesse initiale
col_mu = xl_sheet.col(1) #Attribut la colone 2 au coef de friction
col_m  = xl_sheet.col(2) #Attribut la colone 3 a la masse
col_l  = xl_sheet.col(3) #Attribut la colone 4 a la longueur du vehicule
col_cg = xl_sheet.col(4) #Attribut la colone 5 a la position du centre de masse
col_u  = xl_sheet.col(5) #Attribut la colone 6 a la manoeuvre a faire



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
count2 = 0
X_list_v = []
Y_list_v = []
X_list_l = []
Y_list_l = []
X_vicon_raw = []
Y_vicon_raw = []
X_vic_start = []
Y_vic_start = []
mu_list = []
vi_list = []
u_list = []
l_list = []
bagNumber_list = []

for bagFile in listOfBagFiles:
	count += 1
	print "reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile
	#access bag
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename
	bagNumber = ''.join([n for n in bagName if n.isdigit()])

	# Read params of the test in excel sheet according to bag number
	v_i = col_vi[int(bagNumber)].value
	mu  = col_mu[int(bagNumber)].value
	m   = col_m[int(bagNumber)].value
	l   = col_l[int(bagNumber)].value
	cg  = col_cg[int(bagNumber)].value
	u   = col_u[int(bagNumber)].value

	#Geometrical params of the vehicle
	width = 0.28
	b_length = 0.24
	diff_length = l-0.35
	f_length = 0.32+diff_length
	g = 9.81

	#get list of topics from the bag
	listOfTopics = []
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
	V = []
	k_encd = 0
	trigger = 1
	trigger_vic = 1
	trigger_las = 1
	trigger_las_vic = 1

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
		if (topic == "/debug"):
			V.append(msg.data[1])


	# FIND LASER POSITION AND ANGLE AT FIRST VICON MSG
	first_vicon_time = t_vic[0]

	# INTERPOLATION POUR LA POSITION INITIALE DU LASER_SCAN_MATCHER
	for i in range(len(X_las)):

		if (t_las[i]>first_vicon_time and trigger_las_vic ==1):
			t_las_over = t_las[i]
			X_las_over = X_las[i]
			Y_las_over = Y_las[i]
			theta_las_over = theta_las[i]
			k_las = i-1
			trigger_las_vic = 0

	t_las_under = t_las[k_las]
	X_las_under = X_las[k_las]
	Y_las_under = Y_las[k_las]
	theta_las_under = theta_las[k_las]


	X_las_ini = X_las_under+(first_vicon_time-t_las_under)*(X_las_over-X_las_under)/(t_las_over-t_las_under)+0.09
	Y_las_ini = Y_las_under+(first_vicon_time-t_las_under)*(Y_las_over-Y_las_under)/(t_las_over-t_las_under)
	theta_las_ini = theta_las_under+(first_vicon_time-t_las_under)*(theta_las_over-theta_las_under)/(t_las_over-t_las_under)+0.048

	# TRANSFORM VICON POSITION IN LASER FRAME
	
	for i in range(len(X_vic)):
		X_vic_in_las  = X_vic[i]*np.cos(theta_las_ini)-Y_vic[i]*np.sin(theta_las_ini)
		Y_vic_in_las  = X_vic[i]*np.sin(theta_las_ini)+Y_vic[i]*np.cos(theta_las_ini)
		theta_vic_in_las = (theta_vic[i]-theta_las_ini)

		X_v_real.append(X_vic_in_las+X_las_ini)
		Y_v_real.append(Y_vic_in_las+Y_las_ini)
	

			
	X_list_v.append(X_v_real)
	Y_list_v.append(Y_v_real)

	X_vicon_raw.append(X_vic)
	Y_vicon_raw.append(Y_vic)


	X_list_l.append(X_las)
	Y_list_l.append(Y_las)

	X_vic_start.append(X_las_ini)
	Y_vic_start.append(Y_las_ini)

	bagNumber_list.append(bagNumber)

	bag.close()


for i in range(len(X_list_v)):
	plt.figure(i)
	plt.plot(X_vic_start[i],Y_vic_start[i],'og')
	plt.plot(X_list_v[i],Y_list_v[i],'.b', label='Position vicon')
	#plt.plot(X_vicon_raw[i],Y_vicon_raw[i],'--k', label='Position vicon raw')
	plt.plot(X_list_l[i],Y_list_l[i],'.r', label='Position laser')
	plt.title(bagNumber_list[i])
	plt.xlabel('X_position (m)')
	plt.ylabel('Y_position (m)')
	plt.axis('equal')
	plt.legend()


plt.show()

print "Done reading all " + numberOfFiles + " bag files."



