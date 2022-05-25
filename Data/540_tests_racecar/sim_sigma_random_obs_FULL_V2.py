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
wb = xlsxwriter.Workbook('/home/ubuntu/catkin_ws/src/research_racecar/bagfiles/data_excel/vehicule1_sigma_FULL_100.xlsx')
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
    

    # Standard deviation*3
    sigma_x = 0.0418*3
    sigma_y = 0.0337*3

    #Geometrical params of the vehicle
    width = 0.28
    f_length = 0.30
    b_length = 0.22
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

		obs_x = (random.randrange(1000,15000,1)*0.0001)
		distance_obs = (obs_x+f_length)
		obs_y = (random.randrange(100,10000,1)*0.0001)

		shortest_dist = 1000     # Set a very high shortest_dist
		count2 += 1              # Total nbr of Sim

		#Compute dimensionless numbers (the ones used now are those chosen for their strong physical meanings, migth want to try pi theorem tho)
		pi1            = (obs_x*g*mu)/(v_i**2)                                  # Limite dynamique longitudinale
		pi2            = (mu*g*(obs_x**2+obs_y**2))/(2*obs_y*v_i**2)            # Limite dynamique laterale

		success = 1

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



			# Check if obstacle passes through the rectangle
			#Triangle P1-CG-P2
			t1l1 = np.sqrt((P1_x-P2_x)**2+(P1_y-P2_y)**2)
			t1l2 = np.sqrt((P1_x-distance_obs)**2+(P1_y-obs_y)**2)
			t1l3 = np.sqrt((distance_obs-P2_x)**2+(obs_y-P2_y)**2)
			s1   = (t1l1+t1l2+t1l3)/2
			area1 = np.sqrt(s1*(s1-t1l1)*(s1-t1l2)*(s1-t1l3))

			#Triangle P2-CG-P3
			t2l1 = np.sqrt((P3_x-P2_x)**2+(P3_y-P2_y)**2)
			t2l2 = np.sqrt((P3_x-distance_obs)**2+(P3_y-obs_y)**2)
			t2l3 = np.sqrt((distance_obs-P2_x)**2+(obs_y-P2_y)**2)
			s2   = (t2l1+t2l2+t2l3)/2
			area2 = np.sqrt(s2*(s2-t2l1)*(s2-t2l2)*(s2-t2l3))

			#Triangle P3-CG-P4
			t3l1 = np.sqrt((P3_x-P4_x)**2+(P3_y-P4_y)**2)
			t3l2 = np.sqrt((P3_x-distance_obs)**2+(P3_y-obs_y)**2)
			t3l3 = np.sqrt((distance_obs-P4_x)**2+(obs_y-P4_y)**2)
			s3   = (t3l1+t3l2+t3l3)/2
			area3 = np.sqrt(s3*(s3-t3l1)*(s3-t3l2)*(s3-t3l3))

			#Triangle P4-CG-P1
			t4l1 = np.sqrt((P1_x-P4_x)**2+(P1_y-P4_y)**2)
			t4l2 = np.sqrt((P1_x-distance_obs)**2+(P1_y-obs_y)**2)
			t4l3 = np.sqrt((distance_obs-P4_x)**2+(obs_y-P4_y)**2)
			s4   = (t4l1+t4l2+t4l3)/2
			area4 = np.sqrt(s4*(s4-t4l1)*(s4-t4l2)*(s4-t4l3))

			#Rectangle area
			area5 = t1l1*t2l1

			#Check if triangle's areas sum is greater than rectangle area
			if ((area1+area2+area3+area4)==area5):
				success = 0

		print(success)



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



		
wb.close()
print "Done reading all " + numberOfFiles + " bag files."