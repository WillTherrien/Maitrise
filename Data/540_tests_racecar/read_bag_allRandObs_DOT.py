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

def movingAverageFilter(numbers, window_size):


    moving_averages = []
    i = 0
    while i < len(numbers) - window_size + 1:

        this_window = numbers[i : i + window_size]
        window_average = sum(this_window) / window_size
        moving_averages.append(window_average)
        i += 1
    return moving_averages

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
wb = xlsxwriter.Workbook('/home/ubuntu/catkin_ws/src/research_racecar/bagfiles/data_excel/short_DOT_100.xlsx')
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

nbrOfSimPerBag = 100


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
    b_length = 0.13
    diff_length = l-0.35
    f_length = 0.43+diff_length
    g = 9.81

    #get list of topics from the bag
    listOfTopics = []
    X = []
    Y = []
    theta = []
    read_v = 0
    k = 0
    for topic, msg, t in bagContents:
	if (topic == "/prop_sensors"):
	    read_v = msg.data[1]*0.68
        if (topic == "/states"):
	    if(msg.pose.position.x > 2.4 and k == 0):
	       k=1
               v_real = read_v
            X.append(msg.pose.position.x)
            Y.append(msg.pose.position.y)
            quat = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
            theta.append(tf.transformations.euler_from_quaternion(quat)[2])
            
    #Filter position
    X_filtered = movingAverageFilter( X, 25)
    Y_filtered = movingAverageFilter( Y, 25)
    theta_filtered = movingAverageFilter( theta, 25)
    X = []
    Y = []
    theta = []
    X = X_filtered
    Y = Y_filtered
    theta = theta_filtered

    #Determiner la vitesse du vehicule grace au vicon au moment de la manoeuvre
    vicon_speed = []
    dt = float(1.0/187.0)
    for i in range(1, len(X)):
	vicon_speed.append((X[i]-X[i-1])/dt)
    vicon_speed_filtered = movingAverageFilter( vicon_speed, 25) 
    vicon_speed = []
    vicon_speed = vicon_speed_filtered
    k2 = 0
    for i in range(0,len(vicon_speed)):
	if(X[i] > 2.4 and k2 == 0):
		k2 = 1
		v_real_vicon = vicon_speed_filtered[i]
    bag.close()


    for j in range(nbrOfSimPerBag):

		obs_x = (random.randrange(1000,10000,1)*0.0001)
		distance_obs = (obs_x+2.5+f_length)
		obs_y = (random.randrange(100,5000,1)*0.0001)

		shortest_dist = 1000 #set a very high shortest_dist
		count2 += 1 #Total nbr of Sim

		#Compute dimensionless numbers (the ones used now are those chosen for their strong physical meanings, migth want to try pi theorem tho)
		#pi1 = (self.d*self.T_max)/(2*self.Vx_i*self.r_w*self.m)
		#pi2 = (2*self.d*self.g*self.mu_s)/(Vx**2)
		pi3_real_vicon = (obs_x*g*mu)/(v_real_vicon**2)
		pi3_real       = (obs_x*g*mu)/(v_real**2)
		pi3            = (obs_x*g*mu)/(v_i**2)
		#pi4 = self.delta_max/np.arcsin(2*(self.a+self.b)*self.y/(self.d**2+self.y**2))
		pi5_real_vicon = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_real_vicon**2)
		pi5_real       = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_real**2)
		pi5            = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_i**2)

		for i in range(len(X)):


			#Vehicle is represented by a single dot


			#Compute distance between each corners of the car and the obstacle
			if (Y[i]>obs_y):
				diff_x1 = distance_obs-(X[i]+f_length*np.cos(theta[i]))
				#diff_x1 = distance_obs-X[i]
				diff_y1 = obs_y-Y[i]
				dist1   = np.sqrt(diff_x1**2+diff_y1**2)
			else:
				if (X[i]>distance_obs):
					dist1 = 0
				else:
					diff_x1 = distance_obs-(X[i]+f_length*np.cos(theta[i]))
					#diff_x1 = distance_obs-X[i]
					diff_y1 = 0
					dist1   = np.sqrt(diff_x1**2+diff_y1**2)
				


			#Keep the shortest distance between corners and the obstacle at a given time
			dist_min = dist1

			#Keep shortest distance throughout time
			if(dist_min<shortest_dist):
				shortest_dist = dist_min
			if(shortest_dist >= 0.25):
				recal_dist = 0.25
			else: 
				recal_dist = shortest_dist

			if (shortest_dist > 0.00):
				success = 1
			else:
				success = 0
				recal_dist = 0

		sheet.write(count2,0,u)
		sheet.write(count2,1,pi3_real)
		sheet.write(count2,2,pi5_real)
		sheet.write(count2,3,obs_x)
		sheet.write(count2,4,obs_y)
		sheet.write(count2,5,v_real)
		sheet.write(count2,6,mu)
		sheet.write(count2,7,m)
		sheet.write(count2,8,cg)
		sheet.write(count2,9,l)
		sheet.write(count2,10,recal_dist)
		sheet.write(count2,11,success)
		sheet.write(count2,12,bagNumber)
		sheet.write(count2,13,shortest_dist)
		sheet.write(count2,14,v_i)
		sheet.write(count2,15,pi3)
		sheet.write(count2,16,pi5)
		sheet.write(count2,17,v_real_vicon)
		sheet.write(count2,18,pi3_real_vicon)
		sheet.write(count2,19,pi5_real_vicon)

		
wb.close()
print "Done reading all " + numberOfFiles + " bag files."
