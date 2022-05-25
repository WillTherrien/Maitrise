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


###############################################################
#                SIMULATION FOR NEW POINT                     #
###############################################################



v_i = 3.75
l = 1.5
mu = 0.4
m = 11.35
cg = 0.88
a_u = 0.8*9.81
delta = 0.314
w = 0.2

# Compute rear and front normal forces    
N_r = m/(cg+1)*9.81
N_f = m*9.81-N_r

b = N_f/(m*9.81)*l
a = l-b
Iz = 1.00/12.00*m*(w**2+l**2)

slip_max = 0.02

v_x = v_i
v_y = 0.0
dtheta = 0.0
X = 0.0
Y = 0.0
theta = 0.0
omegaR = v_i
dt = 0.00001
test_X = []
test_Y = []
test_T = []
test_X.append(0)
test_Y.append(0)
test_T.append(0)


while (v_x>0.0 and theta<np.pi/2):
    # Compute rear wheel deceleration according to chosen manoeuvre
    omegaR = omegaR-a_u*dt
    if omegaR < 0:
        omegaR = 0

    # Calculate longitudinal slip accordign to wheel velocity and vehicle inertial speed
    if v_x == 0.0:
        slip_x_r = 0.0
    else:
        slip_x_r = (omegaR-v_x)/v_x
    slip_x_f = 0.0             #Front wheel is free

    # Calculate angular slip
    if v_x == 0:
        slip_a_r = 0.0
        slip_a_f = 0.0
    else:
        slip_a_r = -np.arctan((v_y-b*dtheta)/v_x)
        slip_a_f = delta-np.arctan((v_y+a*dtheta)/v_x)
    
    # Longitudinal stiffness
    Cs_f = N_f*mu/slip_max
    Cs_r = N_r*mu/slip_max
    
    # Cornering stiffness
    Ca_f = N_f*0.165*57.29578
    Ca_r = N_r*0.165*57.29578
    

    if slip_x_f > -0.02:
        Fx_f = Cs_f*slip_x_f
    else:
        Fx_f = -N_f*mu
    if slip_x_r > -0.02:
        Fx_r = Cs_r*slip_x_r
    else:
        Fx_r = -N_r*mu
        
    if (slip_a_f<0.1):
        Fy_f = Ca_f*slip_a_f
    else:
        Fy_f = N_f*mu
    if (slip_a_r<0.1):
        Fy_r = Ca_r*slip_a_r
    else:
        Fy_r = N_r*mu
                    
    # Compute states
    """ 
    Equations of Motion
    -------------------------
    STATES_DERIVATIVE
    dv_x    = (F_xf*cos(delta)-F_yf*sin(delta)+F_xr)/m-v_y*dtheta   "longitudinal force sum (F_x = m*dv_x) gives longitudinal acceleration dv_x"
    dv_y    = (F_yf*cos(delta)+F_xf*sin(delta)+F_yr)/m - v_x*dtheta "lateral force sum (F_y = m*dv_y) gives lateral acceleration dv_y"
    ddtheta = (a*(F_yf*cos(delta)+F_xf*sin(delta))-b*F_yr)/Iz       "Torque sum at mass center (T = I*ddtheta) gives the angular acceleration of the vehicle ddtheta"
    dtheta  = dtheta                                                "dtheta is already a state which is the yaw rate"
    dX      = v_x*cos(theta)-v_y*sin(theta)                         "To obtain cartesian position"
    dY      = v_x*sin(theta)+v_y*cos(theta)


    INPUTS 
    delta is the steering angle (rad)
    omega*R is the front wheel linear velocity (m/s)


    Where 
    Fx_f is the longitudinal force applied parallel with the front wheel (N)
    Fx_r is the longitudinal force applied parallel with the rear wheel (N)
    Fy_f is the lateral force applied perpendicularly with the front wheel (N)
    Fy_r is the lateral force applied perpendicularly with the rear wheel (N)
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
    v_x =  ((Fx_f*np.cos(delta)-Fy_f*np.sin(delta)+Fx_r)/m+v_y*dtheta)*dt+v_x
    if v_x < 0.05:
        v_x = 0.0
    v_y =  ((Fy_f*np.cos(delta)+Fx_f*np.sin(delta)+Fy_r)/m - v_x*dtheta)*dt+v_y
    dtheta = ((a*(Fy_f*np.cos(delta)+Fx_f*np.sin(delta))-b*Fy_r)/Iz)*dt+dtheta
    theta  = dtheta*dt+theta
    X = (v_x*np.cos(theta)-v_y*np.sin(theta))*dt+X
    Y = (v_x*np.sin(theta)+v_y*np.cos(theta))*dt+Y
    test_X.append(X)
    test_Y.append(Y)
    test_T.append(theta)

pi1 = X/l
pi2 = Y/l
pi3 = theta
pi4 = a_u*l/v_i**2
pi5 = delta
pi6 = mu
pi7 = cg
#pi8 = l/w
#pi9 = a_u/9.81
#pi10 = 9.81*mu/((cg+1)*a_u)
pi11 = 9.81*mu*l/(v_i**2*np.tan(delta))
pi12 = 9.81*l/v_i**2



print('Real values from sim [X,Y,theta]: [%.3f,%.3f,%.3f]' % (X,Y,theta))

###############################################################
#               READ DATA FROM EXCEL FILE                     #
###############################################################                                       
#Load data set
data = pd.read_excel('excel_data/v4_data_modif.xlsx',index_col=False)
#data["pi10"] = 9.81*data['pi6']/((data['pi7']+1)*data['a'])
data["pi11"] = 9.81*data['pi6']*data['l']/(data['v_i']**2*np.tan(data['pi5']))
data["pi12"] = 9.81*data['l']/data['v_i']**2




###############################################################
#             CREATE AND TRAIN PHYSICAL MODELS                #
###############################################################

# PHYSICAL MODELS
mae_X_p = 0.0
mae_Y_p = 0.0
mae_T_p = 0.0


#Only use physical input (v_i, length, a and delta)

X_p = data.drop(["u","pi1","pi2","pi3","pi4","pi5","pi8","pi9","X","Y","theta","pi11","pi12"],axis=1)
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
row = [pi4,pi5,pi6,pi7,pi11,pi12]
new_data_a = [row]

# make a prediction
hat_X_a = model_X_a.predict(new_data_a)
hat_Y_a = model_Y_a.predict(new_data_a)
hat_T_a = model_T_a.predict(new_data_a)
# summarize prediction
print('Predicted dimensionless [X,Y,theta]: [%.3f,%.3f,%.3f]' % (hat_X_a*l,hat_Y_a*l,hat_T_a))

plt.figure(1)
plt.plot(X,Y,'or', label='SIMULATION ')
plt.plot(hat_X_a*l,hat_Y_a*l,'sb', label='DIMENSIONLESS')
plt.plot(hat_X_p,hat_Y_p,'xg', label='PHYSICAL')
plt.title("Trajectoires \n Decel: "+str(a_u)+"m/s**2, Steering: "+str(round(delta,3))+"rad , Vitesse: "+str(v_i)+", Mu: "+str(mu))
plt.arrow(X, Y, 0.1*np.cos(theta), 0.1*np.sin(theta),head_width=0.02,ec='r',fc='r')
plt.arrow(float(hat_X_a*l), float(hat_Y_a*l), 0.1*np.cos(float(hat_T_a)), 0.1*np.sin(float(hat_T_a)),head_width=0.02,ec='b',fc='b')
plt.arrow(float(hat_X_p), float(hat_Y_p), 0.1*np.cos(float(hat_T_p)), 0.1*np.sin(float(hat_T_p)),head_width=0.02,ec='g',fc='g')
R_sim = (X**2+Y**2)/(2*Y)
y_r = 0.0
X_R = []
Y_R = []
x_r = 0.0
while x_r<X:
    X_R.append(x_r)
    Y_R.append(y_r)
    y_r+=0.001
    x_r = np.sqrt(2*y_r*R_sim-y_r**2)
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
plt.plot(X_R,Y_R,'--r')
plt.plot(X_aR,Y_aR,'--b')
plt.plot(X_pR,Y_pR,'--g')

plt.xlabel('X_position (m)')
plt.ylabel('Y_position (m)')
plt.axis("equal")
plt.legend()
plt.show()

















