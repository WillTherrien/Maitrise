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
X_list = []
Y_list = []
mu_list = []
vi_list = []
u_list = []
l_list = []

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
			print( msg.pose.position.x)
			X.append(msg.pose.position.x)
			Y.append(msg.pose.position.y)
			quat = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
			theta.append(tf.transformations.euler_from_quaternion(quat)[2])
	X_list.append(X)
	Y_list.append(Y)
	mu_list.append(mu)
	vi_list.append(v_i)
	u_list.append(u)
	l_list.append(l)

	bag.close()

for i in range(len(X_list)):

	if(u_list[i] == 1):
		plt.figure(1)
		plt.plot(X_list[i],Y_list[i],'-b', label='Brake 100%')
		plt.title('Comparaison des manoeuvres')
		plt.xlabel('X_position (m)')
		plt.ylabel('Y_position (m)')
		if(vi_list[i] == 1):
			if(mu_list[i] == 0.2):
				plt.figure(6)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% brake avec vitesse initiale de 1 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(6)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(6)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 2):
			if(mu_list[i] == 0.2):
				plt.figure(7)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% brake avec vitesse initiale de 2 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(7)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(7)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 3):
			if(mu_list[i] == 0.2):
				plt.figure(8)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% brake avec vitesse initiale de 3 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(8)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(8)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()		
	if(u_list[i] == 2):
		plt.figure(1)
		plt.plot(X_list[i],Y_list[i],'-r', label = 'Turn 33%')
		if(vi_list[i] == 1):
			if(mu_list[i] == 0.2):
				plt.figure(9)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 33% tourne avec vitesse initiale de 1 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(9)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(9)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 2):
			if(mu_list[i] == 0.2):
				plt.figure(10)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 33% tourne avec vitesse initiale de 2 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(10)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(10)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 3):
			if(mu_list[i] == 0.2):
				plt.figure(11)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 33% tourne avec vitesse initiale de 3 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(11)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(11)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()	
	if(u_list[i] == 3):
		plt.figure(1)
		plt.plot(X_list[i],Y_list[i],'-g', label = 'Turn 66%')
		if(vi_list[i] == 1):
			if(mu_list[i] == 0.2):
				plt.figure(12)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne avec vitesse initiale de 1 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(12)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(12)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 2):
			if(mu_list[i] == 0.2):
				plt.figure(13)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne avec vitesse initiale de 2 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(13)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(13)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 3):
			if(mu_list[i] == 0.2):
				plt.figure(14)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne avec vitesse initiale de 3 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(14)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(14)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()	
	if(u_list[i] == 4):
		plt.figure(1)
		plt.plot(X_list[i],Y_list[i],'-y', label = 'Turn 100%')
		if(vi_list[i] == 1):
			if(mu_list[i] == 0.2):
				plt.figure(15)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% tourne avec vitesse initiale de 1 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(15)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(15)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 2):
			if(mu_list[i] == 0.2):
				plt.figure(16)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% tourne avec vitesse initiale de 2 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(16)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(16)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 3):
			if(mu_list[i] == 0.2):
				plt.figure(17)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 100% tourne avec vitesse initiale de 3 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(17)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(17)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()	
	if(u_list[i] == 5):
		plt.figure(1)
		plt.plot(X_list[i],Y_list[i],'-m', label = 'Turn 66% and brake')
		if(vi_list[i] == 1):
			if(mu_list[i] == 0.2):
				plt.figure(18)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne & brake avec vitesse initiale de 1 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(18)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(18)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 2):
			if(mu_list[i] == 0.2):
				plt.figure(19)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne & brake avec vitesse initiale de 2 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(19)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(19)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
		if(vi_list[i] == 3):
			if(mu_list[i] == 0.2):
				plt.figure(20)
				plt.plot(X_list[i],Y_list[i],'-b',label='mu = 0.2')
				plt.title('Manoeuvre 66% tourne & brake avec vitesse initiale de 3 m/s')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(mu_list[i] == 0.4):
				plt.figure(20)
				plt.plot(X_list[i],Y_list[i],'-r',label='mu = 0.4')
			if(mu_list[i] == 0.9):
				plt.figure(20)
				plt.plot(X_list[i],Y_list[i],'-g',label='mu = 0.9')
			plt.legend()
	plt.figure(1)	
	plt.legend()



	if(mu_list[i] == 0.2):
		plt.figure(2)
		plt.plot(X_list[i],Y_list[i],'-b',label='Mu = 0.2')
		plt.title('Comparaison des coefficients de friction')
		plt.xlabel('X_position (m)')
		plt.ylabel('Y_position (m)')
		if(vi_list[i] == 1):
			plt.figure(3)
			plt.plot(X_list[i],Y_list[i],'-b',label='v = 1.0')
			plt.title('Comparaison des vitesses avec une coef. de fric. de 0.2')
			plt.xlabel('X_position (m)')
			plt.ylabel('Y_position (m)')
			if(u_list[i] == 1):
				plt.figure(21)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 1 m/s, mu = 0.2')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(21)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(21)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(21)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(21)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		if(vi_list[i] == 2):
			plt.figure(3)
			plt.plot(X_list[i],Y_list[i],'-r',label='v = 2.0')
			if(u_list[i] == 1):
				plt.figure(22)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 2 m/s, mu = 0.2')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(22)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(22)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(22)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(22)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		if(vi_list[i] == 3):
			plt.figure(3)
			plt.plot(X_list[i],Y_list[i],'-g',label='v = 3.0')
			if(u_list[i] == 1):
				plt.figure(23)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 3 m/s, mu = 0.2')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(23)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(23)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(23)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(23)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		plt.figure(3)
		plt.legend()
	if(mu_list[i] == 0.4):
		plt.figure(2)
		plt.plot(X_list[i],Y_list[i],'-r',label='Mu = 0.4')
		if(vi_list[i] == 1):
			plt.figure(4)
			plt.plot(X_list[i],Y_list[i],'-b',label='v = 1.0')
			plt.title('Comparaison des vitesses avec une coef. de fric. de 0.4')
			plt.xlabel('X_position (m)')
			plt.ylabel('Y_position (m)')
			if(u_list[i] == 1):
				plt.figure(24)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 1 m/s, mu = 0.4')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(24)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(24)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(24)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(24)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		if(vi_list[i] == 2):
			plt.figure(4)
			plt.plot(X_list[i],Y_list[i],'-r',label='v = 2.0')
			if(u_list[i] == 1):
				plt.figure(25)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 2 m/s, mu = 0.4')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(25)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(25)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(25)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(25)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		if(vi_list[i] == 3):
			plt.figure(4)
			plt.plot(X_list[i],Y_list[i],'-g',label='v = 3.0')
			if(u_list[i] == 1):
				plt.figure(26)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 3 m/s, mu = 0.4')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(26)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(26)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(26)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(26)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		plt.figure(4)
		plt.legend()
	if(mu_list[i] == 0.9):
		plt.figure(2)
		plt.plot(X_list[i],Y_list[i],'-g',label='Mu = 0.9')
		if(vi_list[i] == 1):
			plt.figure(5)
			plt.plot(X_list[i],Y_list[i],'-b',label='v = 1.0')
			plt.title('Comparaison des vitesses avec une coef. de fric. de 0.9')
			plt.xlabel('X_position (m)')
			plt.ylabel('Y_position (m)')
			if(u_list[i] == 1):
				plt.figure(27)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 1 m/s, mu = 0.9')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(27)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(27)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(27)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(27)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
					
			plt.legend()
		if(vi_list[i] == 2):
			plt.figure(5)
			plt.plot(X_list[i],Y_list[i],'-r',label='v = 2.0')
			if(u_list[i] == 1):
				plt.figure(28)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 2 m/s, mu = 0.9')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(28)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(28)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(28)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(28)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
			plt.legend()
		if(vi_list[i] == 3):
			plt.figure(5)
			plt.plot(X_list[i],Y_list[i],'-g',label='v = 3.0')
			if(u_list[i] == 1):
				plt.figure(29)
				plt.plot(X_list[i],Y_list[i],'-b',label='u = 100% Brake')
				plt.title('Comparaison des manoeuvres v = 3 m/s, mu = 0.9')
				plt.xlabel('X_position (m)')
				plt.ylabel('Y_position (m)')
			if(u_list[i] == 2):
				plt.figure(29)
				plt.plot(X_list[i],Y_list[i],'-r',label='u = 33% Turn')
			if(u_list[i] == 3):
				plt.figure(29)
				plt.plot(X_list[i],Y_list[i],'-g',label='u = 66% Turn')
			if(u_list[i] == 4):
				plt.figure(29)
				plt.plot(X_list[i],Y_list[i],'-k',label='u = 100% Turn')
			if(u_list[i] == 5):
				plt.figure(29)
				plt.plot(X_list[i],Y_list[i],'-m',label='u = 66% Turn & brake')
				if(l_list[i] == 0.35):
					plt.figure(30)
					plt.title('Comparaison des rayons de courbures a faible vitesse et haut coefficient de friction')
					plt.xlabel('X_position (m)')
					plt.ylabel('Y_position (m)')
					plt.plot(X_list[i],Y_list[i],'-b',label='length = 0.35m')
				if(l_list[i] == 0.40):
					plt.figure(30)
					plt.plot(X_list[i],Y_list[i],'-r',label='length = 0.40m')
				plt.legend()
			plt.legend()
		plt.figure(5)
		plt.legend()
	plt.figure(2)
	plt.legend()

plt.show()

print "Done reading all " + numberOfFiles + " bag files."

