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
workbook = xlrd.open_workbook('/home/ubuntu/Desktop/Xmass_tests.xlsx')
# Choose sheet
xl_sheet = workbook.sheet_by_index(0)
# Read particular columns of a sheet
col_vi = xl_sheet.col(0) #Attribut la colone 1 a la vitesse initiale
col_mu = xl_sheet.col(1) #Attribut la colone 2 au coef de friction
col_m  = xl_sheet.col(2) #Attribut la colone 3 a la masse
col_l  = xl_sheet.col(3) #Attribut la colone 4 a la longueur du vehicule
col_cg = xl_sheet.col(4) #Attribut la colone 5 a la position du centre de masse
col_u  = xl_sheet.col(5) #Attribut la colone 6 a la manoeuvre a faire
col_au = xl_sheet.col(7)
col_delta = xl_sheet.col(8)

# Create a new workbook
wb = xlsxwriter.Workbook('/home/ubuntu/catkin_ws/src/research_racecar/bagfiles/data_excel/xmass_sigma_FULL_1000.xlsx')
sheet = wb.add_worksheet('Sheet1')	
sheet.write(0,0,"u")
sheet.write(0,1,"pi1")
sheet.write(0,2,"pi2")
sheet.write(0,3,"obs_x")
sheet.write(0,4,"obs_y")
sheet.write(0,5,"v")
sheet.write(0,6,"mu")
sheet.write(0,7,"m")
sheet.write(0,8,"cg")
sheet.write(0,9,"l")
sheet.write(0,10,"y")
sheet.write(0,11,"Bag#")
sheet.write(0,12,"dist")
sheet.write(0,13,"a_u")
sheet.write(0,14,"delta")

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

nbrOfSimPerBag = 1000


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
    a_u = col_au[int(bagNumber)].value
    delta = col_delta[int(bagNumber)].value


    # Standard deviation*3
    sigma_x = 0.0
    sigma_y = 0.0
    #sigma_x = 0.0418*3
    #sigma_y = 0.0337*3


    #Geometrical params of the vehicle
    width = 0.57
    f_length = 0.61   # valeur fictive
    b_length = 0.12  # valeur fictive
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
		#pi1            = (obs_x*g*mu)/(v_i**2)                                  # Limite dynamique longitudinale
		a_ness         = v_i**2/(2*obs_x)
		a_mu = ((m/(cg+1))*mu*g)/m
		
		# a retravailler
		a_decel = u*0.1*g
		if (a_decel > a_mu):
			a_adm = a_mu
		else:
			a_adm = a_decel
		pi1 = a_adm/a_ness

		pi2            = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_i**2)            # Limite dynamique laterale

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

			d_front = np.sqrt((f_length+sigma_x)**2+(width/2+sigma_y)**2)
			d_back  = np.sqrt((b_length+sigma_x)**2+(width/2+sigma_y)**2)
			a_1 = np.arctan2(width/2+sigma_y,f_length+sigma_x)+theta[i]
			a_2 = np.pi/2+np.arctan2(b_length+sigma_x,width/2+sigma_y)+theta[i]
			a_3 = np.pi+np.arctan2(width/2+sigma_y,b_length+sigma_x)+theta[i]
			a_4 = 2*np.pi-np.arctan2(width/2+sigma_y,f_length+sigma_x)+theta[i]
			P1_x = X[i] + d_front*np.cos(a_1)
			P1_y = Y[i] + d_front*np.sin(a_1)
			P2_x = X[i] + d_back*np.cos(a_2)
			P2_y = Y[i] + d_back*np.sin(a_2)
			P3_x = X[i] + d_back*np.cos(a_3)
			P3_y = Y[i] + d_back*np.sin(a_3)
			P4_x = X[i] + d_front*np.cos(a_4)
			P4_y = Y[i] + d_front*np.sin(a_4)


			#Compute distance between each corners of the car and the obstacle
			if (P1_y>obs_y):
				diff_x1 = distance_obs-P1_x
				diff_y1 = obs_y-P1_y
				dist1   = np.sqrt(diff_x1**2+diff_y1**2)
			else:
				if (P1_x>distance_obs):
					dist1 = 0
				else:
					diff_x1 = distance_obs-P1_x
					diff_y1 = 0
					dist1   = np.sqrt(diff_x1**2+diff_y1**2)
				
			if (P2_y>obs_y):
				diff_x2 = distance_obs-P2_x
				diff_y2 = obs_y-P2_y
				dist2   = np.sqrt(diff_x2**2+diff_y2**2)
			else:
				if (P2_x>distance_obs):
					dist2 = 0
				else:
					diff_x2 = distance_obs-P2_x
					diff_y2 = 0
					dist2   = np.sqrt(diff_x2**2+diff_y2**2)			
			if (P3_y>obs_y):
				diff_x3 = distance_obs-P3_x
				diff_y3 = obs_y-P3_y
				dist3   = np.sqrt(diff_x3**2+diff_y3**2)
			else:
				if (P3_x>distance_obs):
					dist3 = 0
				else:
					diff_x3 = distance_obs-P3_x
					diff_y3 = 0
					dist3   = np.sqrt(diff_x3**2+diff_y3**2)
			if (P4_y>obs_y):
				diff_x4 = distance_obs-P4_x
				diff_y4 = obs_y-P4_y
				dist4   = np.sqrt(diff_x4**2+diff_y4**2)
			else:
				if (P4_x>distance_obs):
					dist4 = 0
				else:
					diff_x4 = distance_obs-P4_x
					diff_y4 = 0
					dist4   = np.sqrt(diff_x1**2+diff_y4**2)

			#Keep the shortest distance between corners and the obstacle at a given time
			dist_min = min(dist1,dist2,dist3,dist4)

			#Keep shortest distance throughout time
			if(dist_min<shortest_dist):
				shortest_dist = dist_min
			if(shortest_dist >= 0.25):
				recal_dist = 0.25
			else: 
				recal_dist = shortest_dist
			if (shortest_dist > 0):
				success = 1
			else:
				success = 0

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
		sheet.write(count2,13,a_u)
		sheet.write(count2,14,delta)


		
wb.close()
print "Done reading all " + numberOfFiles + " bag files."
