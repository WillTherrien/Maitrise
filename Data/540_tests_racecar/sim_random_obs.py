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
import xlsxwriter
from xlutils.copy import copy
import random



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

# Create a new workbook
wb = xlsxwriter.Workbook('/home/ubuntu/catkin_ws/src/research_racecar/bagfiles/data_excel/vehicule1_DOT_2000.xlsx')
sheet = wb.add_worksheet('Sheet1')	


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

nbrOfSimPerBag = 2000


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
    f_length = 0.30
    g = 9.81

    # Init
    X = []
    Y = []
    theta = []
    X_vic = []
    Y_vic = []
    theta_vic = []
    t_vic     = []
    encd_pos  = []
    t_encd    = []
    trigger = 1
    trigger_vic = 1

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
    X.append(0)
    Y.append(0)
    theta.append(0)
    for i in range(len(X_vic)):
	if (X_vic[i]>X_vic_ini):
		X.append((X_vic[i]-X_vic_ini)*np.cos(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.sin(theta_vic_ini))
		Y.append(-(X_vic[i]-X_vic_ini)*np.sin(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.cos(theta_vic_ini))
		theta.append(theta_vic[i]-theta_vic_ini)
			
            

    bag.close()


    for j in range(nbrOfSimPerBag):

		obs_x = (random.randrange(1000,10000,1)*0.0001)
		distance_obs = (obs_x+f_length)
		obs_y = (random.randrange(100,5000,1)*0.0001)

		shortest_dist = 1000     # Set a very high shortest_dist
		count2 += 1              # Total nbr of Sim

		#Compute dimensionless numbers (the ones used now are those chosen for their strong physical meanings, migth want to try pi theorem tho)
		pi1            = (obs_x*g*mu)/(v_i**2)                                  # Limite dynamique longitudinale
		pi2            = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_i**2)            # Limite dynamique laterale

		for i in range(len(X)):

			#Vehicle is represented by a single dot
			#Compute distance between each corners of the car and the obstacle
			if (Y[i]>obs_y):
				diff_x1 = distance_obs-(X[i]+f_length*np.cos(theta[i]))
				diff_y1 = obs_y-Y[i]
				dist1   = np.sqrt(diff_x1**2+diff_y1**2)
			else:
				if (X[i]>distance_obs):
					dist1 = 0
				else:
					diff_x1 = distance_obs-(X[i]+f_length*np.cos(theta[i]))
					diff_y1 = 0
					dist1   = np.sqrt(diff_x1**2+diff_y1**2)
				


			#Keep the shortest distance between corners and the obstacle at a given time
			dist_min = dist1

			#Keep shortest distance throughout time
			if(dist_min<shortest_dist):
				shortest_dist = dist_min
			#if(shortest_dist >= 0.25):
			#	recal_dist = 0.25
			#else: 
			#	recal_dist = shortest_dist

			if (shortest_dist > 0.00):
				success = 1
			else:
				success = 0
				recal_dist = 0

		sheet.write(count2,0,u)
		sheet.write(count2,1,pi1)
		sheet.write(count2,2,pi2)
		sheet.write(count2,3,obs_x)
		sheet.write(count2,4,obs_y)
		sheet.write(count2,5,v_i)
		sheet.write(count2,6,mu)
		sheet.write(count2,7,m)
		sheet.write(count2,8,cg)
		sheet.write(count2,9,l)
		sheet.write(count2,10,success)
		sheet.write(count2,11,bagNumber)
		sheet.write(count2,12,shortest_dist)


		
wb.close()
print "Done reading all " + numberOfFiles + " bag files."
