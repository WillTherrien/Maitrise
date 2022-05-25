#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 10:15:47 2020

@author: ubuntu
"""
import pandas as pd # data processing
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
from joblib import dump, load
import numpy as np
import matplotlib.pyplot as plt
import rosbag, sys, csv
import xlrd
import os
import tf


###############################################################
#                SIMULATION FOR NEW POINT                     #
###############################################################


# Open workbook
workbook = xlrd.open_workbook('/home/ubuntu/Desktop/limo_tests.xlsx')
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



print('Real values from sim [X,Y,theta]: [%.3f,%.3f,%.3f]' % (X,Y,theta))

###############################################################
#               READ DATA FROM EXCEL FILE                     #
###############################################################                                       
#Load data set
data = pd.read_excel('limo_data.xlsx',index_col=False)

###############################################################
#             CREATE AND TRAIN PHYSICAL MODELS                #
###############################################################

# PHYSICAL MODELS
mae_X_p = 0.0
mae_Y_p = 0.0
mae_T_p = 0.0


#Only use physical input (v_i, length, a and delta)

X_p = data.drop(["u","pi1","pi2","pi3","pi4","pi5","pi8","pi9","X","Y","theta","pi10","pi11","pi12"],axis=1)

X_p = X_p.values



#Only use y as output
y_X_p = data["X"].values
y_Y_p = data["Y"].values
y_T_p = data["theta"].values


#Create models
model_X_p = XGBRegressor()
model_Y_p = XGBRegressor()
model_T_p = XGBRegressor()    

## define model evaluation method
#cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

## evaluate models
#scores_X_p = cross_val_score(model_X_p, X_p, y_X_p, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
#scores_Y_p = cross_val_score(model_Y_p, X_p, y_Y_p, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
#scores_T_p = cross_val_score(model_T_p, X_p, y_T_p, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)

## force scores to be positive
#scores_X_p = absolute(scores_X_p)
#print('Mean MAE: %.3f (%.3f)' % (scores_X_p.mean(), scores_X_p.std()) )
#scores_Y_p = absolute(scores_Y_p)
#print('Mean MAE: %.3f (%.3f)' % (scores_Y_p.mean(), scores_Y_p.std()) )
#scores_T_p = absolute(scores_T_p)
#print('Mean MAE: %.3f (%.3f)' % (scores_T_p.mean(), scores_T_p.std()) )

model_X_p.fit(X_p,y_X_p)
model_Y_p.fit(X_p,y_Y_p)
model_T_p.fit(X_p,y_T_p)

# define new data
row_p = [v_i,l,a_u,delta,pi6,pi7,m]
new_data_p = [row_p]


# make a prediction
hat_X_p = model_X_p.predict(new_data_p)
hat_Y_p = model_Y_p.predict(new_data_p)
hat_T_p = model_T_p.predict(new_data_p)
# summarize prediction
print('Predicted physical [X,Y,theta]: [%.3f,%.3f,%.3f]' % (hat_X_p,hat_Y_p,hat_T_p))

###############################################################
#          CREATE AND TRAIN DIMENSIONLESS MODELS              #
###############################################################

# PHYSICAL MODELS
mae_X_a = 0.0
mae_Y_a = 0.0
mae_T_a = 0.0


#Only use physical input (v_i, length, a and delta)
X_a = data.drop(["u","pi1","pi2","pi3","v_i","delta","l","X","Y","theta","m","a","pi8","pi9"],axis=1)
X_a = X_a.values



#Only use y as output
y_X_a = data["pi1"].values
y_Y_a = data["pi2"].values
y_T_a = data["pi3"].values


#Create models
model_X_a = XGBRegressor()
model_Y_a = XGBRegressor()
model_T_a = XGBRegressor()    

## define model evaluation method
#cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

## evaluate models
#scores_X_a = cross_val_score(model_X_a, X_a, y_X_a, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
#scores_Y_a = cross_val_score(model_Y_a, X_a, y_Y_a, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
#scores_T_a = cross_val_score(model_T_a, X_a, y_T_a, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)

## force scores to be positive
#scores_X_a = absolute(scores_X_a)
#print('Mean MAE: %.3f (%.3f)' % (scores_X_a.mean(), scores_X_a.std()) )
#scores_Y_a = absolute(scores_Y_a)
#print('Mean MAE: %.3f (%.3f)' % (scores_Y_a.mean(), scores_Y_a.std()) )
#scores_T_a = absolute(scores_T_a)
#print('Mean MAE: %.3f (%.3f)' % (scores_T_a.mean(), scores_T_a.std()) )

model_X_a.fit(X_a,y_X_a)
model_Y_a.fit(X_a,y_Y_a)
model_T_a.fit(X_a,y_T_a)

# define new data
row = [pi4,pi5,pi6,pi7,pi10,pi11,pi12]
new_data_a = [row]

# make a prediction
hat_X_a = model_X_a.predict(new_data_a)
hat_Y_a = model_Y_a.predict(new_data_a)
hat_T_a = model_T_a.predict(new_data_a)
# summarize prediction
print('Predicted dimensionless [X,Y,theta]: [%.3f,%.3f,%.3f]' % (hat_X_a*l,hat_Y_a*l,hat_T_a))

plt.figure(1)
plt.plot(X,Y,'or', label='VICON ')
plt.plot(X_v_real,Y_v_real,'--r')
plt.plot(hat_X_a*l,hat_Y_a*l,'sb', label='DIMENSIONLESS')
plt.plot(hat_X_p,hat_Y_p,'xg', label='PHYSICAL')
plt.title("Trajectoires \n Decel: "+str(a_u)+"m/s**2, Steering: "+str(round(delta,3))+"rad , Vitesse: "+str(v_i)+", Mu: "+str(mu))
plt.arrow(X, Y, 0.1*np.cos(theta), 0.1*np.sin(theta),head_width=0.02,ec='r',fc='r')
plt.arrow(float(hat_X_a*l), float(hat_Y_a*l), 0.1*np.cos(float(hat_T_a)), 0.1*np.sin(float(hat_T_a)),head_width=0.02,ec='b',fc='b')
plt.arrow(float(hat_X_p), float(hat_Y_p), 0.1*np.cos(float(hat_T_p)), 0.1*np.sin(float(hat_T_p)),head_width=0.02,ec='g',fc='g')
#R_sim = (X**2+Y**2)/(2*Y)
#y_r = 0.0
#X_R = []
#Y_R = []
#x_r = 0.0
#while x_r<X:
#    X_R.append(x_r)
#    Y_R.append(y_r)
#    y_r+=0.001
#    x_r = np.sqrt(2*y_r*R_sim-y_r**2)
R_adim = (float(hat_X_a*l)**2+float(hat_Y_a*l)**2)/(2*float(hat_Y_a*l))
y_ar = 0.0
X_aR = []
Y_aR = []
x_ar = 0.0
while x_ar<float(hat_X_a*l):
    X_aR.append(x_ar)
    Y_aR.append(y_ar)
    y_ar+=0.001
    x_ar = np.sqrt(2*y_ar*R_adim-y_ar**2)
R_p = (float(hat_X_p)**2+float(hat_Y_p)**2)/(2*float(hat_Y_p))
y_pr = 0.0
X_pR = []
Y_pR = []
x_pr = 0.0
while x_pr<float(hat_X_p):
    X_pR.append(x_pr)
    Y_pR.append(y_pr)
    y_pr+=0.001
    x_pr = np.sqrt(2*y_pr*R_p-y_pr**2)
#plt.plot(X_R,Y_R,'--r')
plt.plot(X_aR,Y_aR,'--b')
plt.plot(X_pR,Y_pR,'--g')

plt.xlabel('X_position (m)')
plt.ylabel('Y_position (m)')
plt.axis("equal")
plt.legend()
plt.show()

















