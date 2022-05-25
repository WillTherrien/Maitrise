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
workbook = xlrd.open_workbook('/home/ubuntu/Desktop/autobus_tests_sim.xlsx')
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
	l   = col_l[int(bagNumber)].value
	cg  = col_cg[int(bagNumber)].value
	u   = col_u[int(bagNumber)].value
	a_u = col_au[int(bagNumber)].value
	delta = col_delta[int(bagNumber)].value*25*np.pi/180


	g = 9.81


    	if (l == 0.345):
		#Geometrical params of the racecar
		width = 0.28
		f_length = 0.42
		b_length = 0.13

    	elif (l == 0.853):
		#Geometrical params of the limo
		width = 0.28
		f_length = 0.91  
		b_length = 0.13  

    	else:
		#Geometrical params of the Xmaxx
		width = 0.57
		f_length = 0.61   
		b_length = 0.12  

    	Nb = m/(1+cg)*g


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

	print(real_omega_t)
	print(real_omega)

			
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

# Init
X = []
Y = []
theta = []
t = []
omega_r = []
slip = []
v = []
Fx = []
    

X.append(0)
Y.append(0)
theta.append(0)
t.append(0)
omega_r.append(v_i)
v.append(v_i)
slip.append(0)
Fx.append(0)

dt = 0.001
    
k = 0

Fr = 0

    """ 
    Equations of Motion
    -------------------------
    STATES_DERIVATIVE
    dv_x    = (F_xf*cos(delta)-F_yf*sin(delta)+F_xr)/m - v_y*dtheta   "longitudinal force sum (F_x = m*dv_x) gives longitudinal acceleration dv_x"
    dv_y    = (F_yf*cos(delta)+F_xf*sin(delta)+F_yr)/m - v_x*dtheta "lateral force sum (F_y = m*dv_y) gives lateral acceleration dv_y"
    ddtheta = (a*(F_yf*cos(delta)+F_xf*sin(delta))-b*F_yr)/Iz       "Torque sum at mass center (T = I*ddtheta) gives the angular acceleration of the vehicle ddtheta"
    dtheta  = dtheta                                                "dtheta is already a state which is the yaw rate"
    dX      = v_x*cos(theta)-v_y*sin(theta)                         "To obtain cartesian position"
    dY      = v_x*sin(theta)+v_y*cos(theta)
    
    ***** DEPENDS DU MODELE DE TIRE COMPLET EX: S=omega/v_x et F_x,F_y = f(F_z,alpha,S et mu) *****
    
    INPUTS 
    delta is the steering angle (rad)
    Wheel's velocity (m/s)
    
    
    Where 
    F_yf is the lateral force applied perpendicularly with the front wheel (N)
    F_yr is the lateral force applied perpendicularly with the rear wheel (N)
    v_y  is the lateral velocity of the mass center (m/s)
    v_x  is the longitudinal velocity of the mass center (m/s)
    delta is the steering angle (rad)
    theta is the yaw angle of the vehicle (rad)
    m     is the mass of the vehicle (kg)
    Iz    is the inertia for a rotation along the z-axis (kg*m^2)
    a     is the distance from the front axle to the mass centre (m)
    b     is the distance from the rear axle to the mass centre (m)
    (X,Y) is the cartesian position of the vehicle
    """

while (v[k] > 0):

	#Compute wheel decel
	wheel_speed = omega_r[k] - a_u*dt
        if (wheel_speed <0 ):
		wheel_speed = 0
	omega_r.append(wheel_speed)
	

	#Compute slip ratio
	slip.append(omega_r[k+1]-v[k])

	#Compute Fx
	if (abs(slip[k+1]) > max_slip):
		Fx.append(Nb*mu)
	else:
		Fx.append(Nb*mu/max_slip*abs(slip[k+1]))

	#Compute new inertial speed
	a = (Fx[k+1]+Fr)/m
	if ((v[k] - a*dt) < 0.001):
		v.append(0)
	else: 
		v.append(v[k] - a*dt)

	#Reconstruct states using bicycle model
	X.append(X[k]+v[k+1]*np.cos(theta[k])*dt)
	Y.append(Y[k]+v[k+1]*np.sin(theta[k])*dt)
	theta.append(theta[k]+v[k+1]*np.tan(delta)/l*dt)

	#Time	
	k += 1
	t.append(dt*k)

X_list.append(X)
Y_list.append(Y)
Fx_list.append(Fx)
slip_list.append(slip)
v_list.append(v)
omegar_list.append(omega_r)
t_list.append(t)



plt.figure(1)
for i in range(len(X_list_v)):

	plt.plot(X_list_v[i],Y_list_v[i],'-b', label='VICON ['+str(round(X_list_v[i][len(X_list_v[i])-1],4))+' : '+str(round(Y_list_v[i][len(Y_list_v[i])-1],4))+']')
	plt.plot(X_list[i],Y_list[i],'--r', label='SIMULATION ['+str(round(X_list[i][len(X_list[i])-1],4))+' : '+str(round(Y_list[i][len(Y_list[i])-1],4))+']')
	plt.title("Trajectoire VICON & SIMULATION \n Manoeuvre: "+str(u_list[i])+", Vitesse: "+str(vi_list[i])+", Mu: "+str(mu_list[i]))
	plt.xlabel('X_position (m)')
	plt.ylabel('Y_position (m)')
	plt.axis("equal")
	plt.legend()

for j in range(len(slip_list)):

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)

	fig.suptitle("Trajectoire SIMULEE \n Manoeuvre: "+str(u_list[j])+", Vitesse: "+str(vi_list[j])+", Mu: "+str(mu_list[j]))

	ax1.plot(t_list[j], v_list[j],  '--b',label="Sim")
	ax1.plot(t_vic_list[j], V_vic_list[j],  '-k',label="Real")
        ax1.set_ylabel('Inertial speed (m/s)')
	ax2.plot(t_list[j], omegar_list[j],  '--r',label="Sim")
	ax2.plot(real_omega_t_list[j], real_omega_list[j], '-k', label="Real")
	ax2.set_ylabel('Omega*R (m/s)')
	ax3.plot(t_list[j], slip_list[j],  '--g',label="Sim")
	ax3.set_ylabel('Slip ratio')
	ax4.plot(t_list[j], Fx_list[j],  '--k',label="Sim")
	ax4.set_ylabel('Fx (N)')
	ax4.set_xlabel('Time (s)')
	ax1.legend(loc=1)
	ax2.legend(loc=1)
	ax3.legend(loc=1)
	ax4.legend(loc=1)
	ax1.set_xlim(0,t_list[j][len(t_list[j])-1]+0.5)
	ax2.set_xlim(0,t_list[j][len(t_list[j])-1]+0.5)
	ax3.set_xlim(0,t_list[j][len(t_list[j])-1]+0.5)
	ax4.set_xlim(0,t_list[j][len(t_list[j])-1]+0.5)

plt.show()

print "Done reading all " + numberOfFiles + " bag files."



