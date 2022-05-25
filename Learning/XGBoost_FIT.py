#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 10:15:47 2020

@author: ubuntu
"""
import xgboost
import pandas as pd # data processing
from numpy import absolute
from pandas import read_csv
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
from joblib import dump, load
import numpy as np

###############################################################
#                SIMULATION FOR NEW POINT                     #
###############################################################
v_i = 10.0
l = 1.5
a = 0.3*9.81
delta = 0.2*45*np.pi/180

print "v_i: "+str(v_i)+"m/s, l: "+str(l)+"m, a: "+str(a/9.81)+"g, delta: "+str(delta)+"rad"

v = v_i
X = 0.0
Y = 0.0
theta = 0.0
dt = 0.01

while (v>0.0 and theta<np.pi/2):
    v = v-a*dt 
    X = v*np.cos(theta)*dt+X
    Y = v*np.sin(theta)*dt+Y
    theta = v*np.tan(delta)/l*dt+theta
        
pi1 = X/l
pi2 = Y/l
pi3 = theta
pi4 = a*l/v_i**2
pi5 = delta


print('Real values from sim [X,Y,theta]: [%.3f,%.3f,%.3f]' % (X,Y,theta))

###############################################################
#               READ DATA FROM EXCEL FILE                     #
###############################################################                                       
#Load data set
data = pd.read_excel('excel_data/v0_data.xlsx',index_col=False)

###############################################################
#             CREATE AND TRAIN PHYSICAL MODELS                #
###############################################################

# PHYSICAL MODELS
mae_X_p = 0.0
mae_Y_p = 0.0
mae_T_p = 0.0


#Only use physical input (v_i, length, a and delta)
X_p = data.drop(["u","pi1","pi2","pi3","pi4","pi5","X","Y","theta"],axis=1)
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
row_p = [v_i,l,a,delta]
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
X_a = data.drop(["u","pi1","pi2","pi3","v_i","delta","a","l","X","Y","theta"],axis=1)
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
row = [pi4,pi5]
new_data_a = [row]

# make a prediction
hat_X_a = model_X_a.predict(new_data_a)
hat_Y_a = model_Y_a.predict(new_data_a)
hat_T_a = model_T_a.predict(new_data_a)
# summarize prediction
print('Predicted dimensionless [X,Y,theta]: [%.3f,%.3f,%.3f]' % (hat_X_a*l,hat_Y_a*l,hat_T_a))
















