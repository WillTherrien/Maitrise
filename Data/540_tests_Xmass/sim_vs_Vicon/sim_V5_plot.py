'''

Written by William Therrien, August 2021

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
workbook = xlrd.open_workbook('/home/ubuntu/Maitrise/Data/540_tests_Xmass/Xmass_tests.xlsx')
# Choose sheet
xl_sheet = workbook.sheet_by_index(0)
# Read particular columns of a sheet
col_vi = xl_sheet.col(0) 
col_mu = xl_sheet.col(1) 
col_m  = xl_sheet.col(2)
col_l  = xl_sheet.col(3)
col_cg = xl_sheet.col(4) 
col_u  = xl_sheet.col(5) 
col_au = xl_sheet.col(7)
col_delta = xl_sheet.col(8)


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
X_list = []
Y_list = []
Fx_list = []
v_list = []
slip_list = []
omegar_list = []
t_list = []
bagNumber_list = []
real_omega_list = []
real_omega_t_list = []
t_vic_list = []
V_vic_list = []

max_slip = 0.02

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
	length   = col_l[int(bagNumber)].value
	cg  = col_cg[int(bagNumber)].value
	u   = col_u[int(bagNumber)].value
	a_u = col_au[int(bagNumber)].value
	delta_fin = col_delta[int(bagNumber)].value*25*np.pi/180


#	g = 9.81
#
#
#    	if (l == 0.345):
#		#Geometrical params of the racecar
#		width = 0.28
#		f_length = 0.42
#		b_length = 0.13
#
#    	elif (l == 0.853):
#		#Geometrical params of the limo
#		width = 0.28
#		f_length = 0.91  
#		b_length = 0.13  
#
#    	else:
#		#Geometrical params of the Xmaxx
#		width = 0.57
#		f_length = 0.61   
#		b_length = 0.12  
#
#    	Nb = m/(1+cg)*g


	#get list of topics from the bag
	listOfTopics = []
	encd_pos = []
	encd_vit = []
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
	real_omega = []
	real_omega_t = []
	t_vic_real = []
	V_vic = []
	k_encd = 0
	trigger = 1
	trigger_vic = 1
	trigger_las = 1

	for topic, msg, t in bagContents:

		if (topic == "/prop_sensors"):
			encd_pos.append(msg.data[0])
			encd_vit.append(msg.data[1])
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
			inc = i 

	# CREATE REAL ANGULAR VELOCITY
	for i in range(inc,len(encd_vit)):
		real_omega.append(encd_vit[i])
		real_omega_t.append(int(str(t_encd[i]-time_trigger))*0.000000001)


			
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
	V_vic.append(v_i)
	t_vic_real.append(0)
	w = 0 
	for i in range(len(X_vic)-1):
		if (X_vic[i]>X_vic_ini):
			
			#X_v_real.append(X_vic[i]-X_vic_ini)
			#Y_v_real.append(Y_vic[i]-Y_vic_ini)
			#theta_v_real.append(theta_vic[i]-theta_vic_ini)
			X_v_real.append((X_vic[i]-X_vic_ini)*np.cos(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.sin(theta_vic_ini))
			Y_v_real.append(-(X_vic[i]-X_vic_ini)*np.sin(theta_vic_ini)+(Y_vic[i]-Y_vic_ini)*np.cos(theta_vic_ini))
			theta_v_real.append(theta_vic[i]-theta_vic_ini)
			t_vic_real.append(int(str(t_vic[i]-time_trigger))*0.000000001)
			V_vic.append((X_v_real[w+1]-X_v_real[w])/0.005)
			w += 1


			
	X_list_v.append(X_v_real)
	Y_list_v.append(Y_v_real)
	u_list.append(u)
	vi_list.append(v_i)
	mu_list.append(mu)
	real_omega_list.append(real_omega)
	real_omega_t_list.append(real_omega_t)
	t_vic_list.append(t_vic_real)
	V_vic_list.append(V_vic)

	bagNumber_list.append(bagNumber)
		

	bag.close()

g = 9.81
nbrObs = 5000
count = 0
all_stop_d =[]
pass_fail = []

slip_max = 0.02
    
    
# Read params of the test in excel sheet according to bag number
u   = u*0.1*g
width = 0.28

    
Fn_r = m/(cg+1)*g
Fn_f = m*g-Fn_r
    
b = Fn_f/(m*g)*length
a = length-b
Iz = 1.00/12.00*m*(width**2*length**2)
    
Cx_f = Fn_f*mu/slip_max
Ca_f = Fn_f*.5*.165*57.29578

        
Cx_r = Fn_r*mu/slip_max
Ca_r = Fn_r*.5*.165*57.29578

    
# Init
X = 0.0
Y = 0.0
v_x = v_i
v_y = 0.0
dtheta = 0.0
theta = 0.0
omegaR = v_i
dist = 0
dt = 0.001
    
X_sim_list = []
Y_sim_list = []
t_sim_list = []
t_sim = 0.0
X_sim_list.append(0)
Y_sim_list.append(0)
t_sim_list.append(0)
delta = 0.0
while (v_x>0):
    
    # Moving steering
    if (delta<delta_fin):
        delta = 0.3*dt+delta
    else:
        delta =delta_fin
    
        
    # Compute rear wheel deceleration according to chosen manoeuvre
    omegaR = omegaR-u*dt
        
    # Calculate longitudinal slip accordign to wheel velocity and vehicle inertial speed
    slip_x_r = (omegaR-v_x)/v_x
    slip_x_f = 0.0             #Front wheel is free

    # Calculate angular slip
    slip_a_r = np.arctan((b*dtheta-v_y)/v_x)
    slip_a_f = -np.arctan((v_y+a*dtheta)/v_x)+delta

    
    Fx_f = -3.0
    Fx_r = Cx_r*slip_x_r
    if ( abs(Fx_r)>Fn_r*mu):
        Fx_r = -Fn_r*mu
    Fy_f = Ca_f*slip_a_f
    if (abs(Fy_f)>Fn_f*mu):
        if(Fy_f>0):
            Fy_f = Fn_f*mu
        else:
            Fy_f = -Fn_f*mu
    Fy_r = Ca_f*slip_a_r
    if (abs(Fy_r)>Fn_r*mu):
        if(Fy_r>0):
            Fy_r = Fn_r*mu
        else:
            Fy_r = -Fn_r*mu
            
    print(Fx_r)
    

            

    v_x =  ((Fx_f*np.cos(delta)-Fy_f*np.sin(delta)+Fx_r)/m+v_y*dtheta)*dt+v_x
    v_y =  ((Fy_f*np.cos(delta)+Fx_f*np.sin(delta)+Fy_r)/m - v_x*dtheta)*dt+v_y
    dtheta = ((a*(Fy_f*np.cos(delta)+Fx_f*np.sin(delta))-b*Fy_r)/Iz)*dt+dtheta
    theta  = dtheta*dt+theta
    X = (v_x*np.cos(theta)-v_y*np.sin(theta))*dt+X
    Y = (v_x*np.sin(theta)+v_y*np.cos(theta))*dt+Y
    X_sim_list.append(X)
    Y_sim_list.append(Y)
    t_sim = t_sim+dt
    t_sim_list.append(t_sim)

X_list.append(X_sim_list)
Y_list.append(Y_sim_list)   
     
plt.figure(1)
for i in range(len(X_list_v)):

	plt.plot(X_list_v[i],Y_list_v[i],'-b', label='VICON ['+str(round(X_list_v[i][len(X_list_v[i])-1],4))+' : '+str(round(Y_list_v[i][len(Y_list_v[i])-1],4))+']')
	plt.plot(X_list[i],Y_list[i],'--r', label='SIMULATION ['+str(round(X_list[i][len(X_list[i])-1],4))+' : '+str(round(Y_list[i][len(Y_list[i])-1],4))+']')
	plt.title("Trajectoire VICON & SIMULATION \n Manoeuvre: "+str(u_list[i])+", Vitesse: "+str(vi_list[i])+", Mu: "+str(mu_list[i]))
	plt.xlabel('X_position (m)')
	plt.ylabel('Y_position (m)')
	plt.axis("equal")
	plt.legend()
    
plt.show()

        
        
        



