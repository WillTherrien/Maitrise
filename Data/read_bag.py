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

# Open workbook
workbook = xlrd.open_workbook('/home/ubuntu/Desktop/excel_test.xlsx')
# Choose sheet
xl_sheet = workbook.sheet_by_index(0)
# Read particular columns of a sheet
col_vi = xl_sheet.col(0) #Attribut la colone 1 a la vitesse initiale
col_mu = xl_sheet.col(1) #Attribut la colone 2 au coef de friction
col_m  = xl_sheet.col(2) #Attribut la colone 3 a la masse
col_l  = xl_sheet.col(3) #Attribut la colone 4 a la longueur du vehicule
col_cg = xl_sheet.col(4) #Attribut la colone 5 a la position du centre de masse
col_u  = xl_sheet.col(5) #Attribut la colone 6 a la manoeuvre a faire

# Creates workbook to write into IF YOU WANNA WRITE IN THE SAME WK THAT YOU LOADED PREVIOUSLY
#wb = copy(workbook) 
#sheet = wb.get_sheet(0)

# Create a new workbook
wb = Workbook()
sheet = wb.add_sheet('Sheet1')	


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
	print "\n press ctrl+c in the next 10 seconds to cancel \n"
	time.sleep(10)
else:
	print "bad argument(s): " + str(sys.argv)	#shouldnt really come up
	sys.exit(1)

count = 0
count2 = 0
obs_x = []
obs_y = []
distance_obs = []
nbrObs = 150

for i in range(nbrObs):
	#Create obstacle (distance and width)
	obs_x.append(random.randrange(50,250,1)*0.01)
	distance_obs.append(obs_x[i]+2.5)
	obs_y.append(random.randrange(1,100,1)*0.01)

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
	X = []
	Y = []
	theta = []
	for topic, msg, t in bagContents:
		if (topic == "/states"):
			X.append(msg.pose.position.x)
			Y.append(msg.pose.position.y)
			quat = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
			theta.append(tf.transformations.euler_from_quaternion(quat)[2])
	bag.close()


	for j in range(len(obs_x)):

		shortest_dist = 1000 #set a very high shortest_dist
		count2 += 1 #Total nbr of Sim

		#Compute dimensionless numbers (the ones used now are those chosen for their strong physical meanings, migth want to try pi theorem tho)
		#pi1 = (self.d*self.T_max)/(2*self.Vx_i*self.r_w*self.m)
		#pi2 = (2*self.d*self.g*self.mu_s)/(Vx**2)
		pi3 = ((obs_x[j]-diff_length)*g*mu)/(v_i**2)
		#pi4 = self.delta_max/np.arcsin(2*(self.a+self.b)*self.y/(self.d**2+self.y**2))
		pi5 = (mu*g*((obs_x[j]-diff_length)**2+obs_y[j]**2))/(2*obs_y[j]*v_i**2)

		for i in range(len(X)):


			#Vehicle is represented by 4 dots at each corner
			# P2                   P1
			#    *               *
			#    d_back      d_front
			#        *     *         
			#          CG
			#        *     *
			#    d_back      d_front
			#   *                *
			# P3                   P4

			d_front = np.sqrt(f_length**2+(width/2)**2)
			d_back  = np.sqrt(b_length**2+(width/2)**2)
			a_1 = np.arctan2(width/2,f_length)+theta[i]
			a_2 = np.pi/2+np.arctan2(b_length,width/2)+theta[i]
			a_3 = np.pi+np.arctan2(width/2,b_length)+theta[i]
			a_4 = 2*np.pi-np.arctan2(width/2,f_length)+theta[i]
			P1_x = X[i] + d_front*np.cos(a_1)
			P1_y = Y[i] + d_front*np.sin(a_1)
			P2_x = X[i] + d_back*np.cos(a_2)
			P2_y = Y[i] + d_back*np.sin(a_2)
			P3_x = X[i] + d_back*np.cos(a_3)
			P3_y = Y[i] + d_back*np.sin(a_3)
			P4_x = X[i] + d_front*np.cos(a_4)
			P4_y = Y[i] + d_front*np.sin(a_4)


			#Compute distance between each corners of the car and the obstacle
			if (P1_y>obs_y[j]):
				diff_x1 = distance_obs[j]-P1_x
				diff_y1 = obs_y[j]-P1_y
				dist1   = np.sqrt(diff_x1**2+diff_y1**2)
			else:
				if (P1_x>distance_obs[j]):
					dist1 = 0
				else:
					diff_x1 = distance_obs[j]-P1_x
					diff_y1 = 0
					dist1   = np.sqrt(diff_x1**2+diff_y1**2)
				
			if (P2_y>obs_y[j]):
				diff_x2 = distance_obs[j]-P2_x
				diff_y2 = obs_y[j]-P2_y
				dist2   = np.sqrt(diff_x2**2+diff_y2**2)
			else:
				if (P2_x>distance_obs[j]):
					dist2 = 0
				else:
					diff_x2 = distance_obs[j]-P2_x
					diff_y2 = 0
					dist2   = np.sqrt(diff_x2**2+diff_y2**2)			
			if (P3_y>obs_y[j]):
				diff_x3 = distance_obs[j]-P3_x
				diff_y3 = obs_y[j]-P3_y
				dist3   = np.sqrt(diff_x3**2+diff_y3**2)
			else:
				if (P3_x>distance_obs[j]):
					dist3 = 0
				else:
					diff_x3 = distance_obs[j]-P3_x
					diff_y3 = 0
					dist3   = np.sqrt(diff_x3**2+diff_y3**2)
			if (P4_y>obs_y[j]):
				diff_x4 = distance_obs[j]-P4_x
				diff_y4 = obs_y[j]-P4_y
				dist4   = np.sqrt(diff_x4**2+diff_y4**2)
			else:
				if (P4_x>distance_obs[j]):
					dist4 = 0
				else:
					diff_x4 = distance_obs[j]-P4_x
					diff_y4 = 0
					dist4   = np.sqrt(diff_x1**2+diff_y4**2)

			#Keep the shortest distance between corners and the obstacle at a given time
			dist_min = min(dist1,dist2,dist3,dist4)

			#Keep shortest distance throughout time
			if(dist_min<shortest_dist):
				shortest_dist = dist_min

			if (shortest_dist > 0):
				success = 1
			else:
				success = 0

		sheet.write(count2,0,u)
		sheet.write(count2,1,pi3)
		sheet.write(count2,2,pi5)
		sheet.write(count2,3,obs_x[j])
		sheet.write(count2,4,obs_y[j])
		sheet.write(count2,5,v_i)
		sheet.write(count2,6,mu)
		sheet.write(count2,7,m)
		sheet.write(count2,8,cg)
		sheet.write(count2,9,l)
		sheet.write(count2,10,shortest_dist)
		sheet.write(count2,11,success)
		sheet.write(count2,12,int(bagNumber))
		#wb.save('/home/ubuntu/Desktop/excel_test_changingObs.xlsx')
		

wb.save('/home/ubuntu/Desktop/excel_test_150obs.xlsx')
print "Done reading all " + numberOfFiles + " bag files."
