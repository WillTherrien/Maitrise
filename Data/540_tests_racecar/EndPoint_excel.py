'''

Written by William Therrien, August 2020

'''
import xlsxwriter
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
workbook = xlrd.open_workbook('/home/ubuntu/Maitrise/Data/540_tests_racecar/racecar_tests.xlsx')
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


wb = xlsxwriter.Workbook('/home/ubuntu/Maitrise/Learning/excel_data/racecar_data.xlsx')
sheet = wb.add_worksheet('Sheet1')	
sheet.write(0,0,"v_i")
sheet.write(0,1,"l")
sheet.write(0,2,"u")
sheet.write(0,3,"a")
sheet.write(0,4,"delta")
sheet.write(0,5,"pi1")
sheet.write(0,6,"pi2")
sheet.write(0,7,"pi3")             
sheet.write(0,8,"pi4")
sheet.write(0,9,"pi5")
sheet.write(0,10,"X")
sheet.write(0,11,"Y")
sheet.write(0,12,"theta")
sheet.write(0,13,"pi6")
sheet.write(0,14,"pi7")
sheet.write(0,15,"pi8")
sheet.write(0,16,"pi9")
sheet.write(0,17,"m")
sheet.write(0,18,"pi10")
sheet.write(0,19,"pi11")
sheet.write(0,20,"pi12")



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
        a_u = col_au[int(bagNumber)].value
        delta = col_delta[int(bagNumber)].value
	delta = delta*25.0*np.pi/180.0
        if delta == 0:
           delta = 0.00001

	#Geometrical params of the vehicle
	w = 0.28
	# Compute rear and front normal forces    
        N_r = m/(cg+1)*9.81
        N_f = m*9.81-N_r
    
        b = N_f/(m*9.81)*l
        a = l-b
        Iz = 1.00/12.00*m*(w**2+l**2)

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




        X = X_v_real[-1]
        Y = Y_v_real[-1]
        theta = theta_v_real[-1]
        pi1 = X/l
        pi2 = Y/l
        pi3 = theta
        pi4 = a_u*l/v_i**2
        pi5 = delta
        pi6 = mu
        pi7 = cg
        #pi8 = l/w
        #pi9 = a_u/9.81
        pi10 = 9.81*mu/((cg+1)*a_u)
        pi11 = 9.81*mu*l/(v_i**2*np.tan(delta))
        pi12 = 9.81*l/v_i**2
			
        sheet.write(count,0,v_i)
        sheet.write(count,1,l)
        sheet.write(count,2,0)
        sheet.write(count,3,a_u)
        sheet.write(count,4,delta)
        sheet.write(count,5,pi1)
        sheet.write(count,6,pi2)     
        sheet.write(count,7,pi3) 
        sheet.write(count,8,pi4)
        sheet.write(count,9,pi5)
        sheet.write(count,10,X)        
        sheet.write(count,11,Y)        
        sheet.write(count,12,theta)
        sheet.write(count,13,pi6) 
        sheet.write(count,14,pi7)
        sheet.write(count,15,0) 
        sheet.write(count,16,0) 
        sheet.write(count,17,m)
        sheet.write(count,18,pi10)
        sheet.write(count,19,pi11)
        sheet.write(count,20,pi12)


		

	bag.close()


wb.close()
print "Done reading all " + numberOfFiles + " bag files."



