#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 10:15:47 2020

@author: ubuntu
"""
import pandas as pd # data processing
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from joblib import dump, load
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap
from xgboost import plot_importance
from matplotlib import pyplot

def MAPE(y_true, y_pred): 
  y_true, y_pred = np.array(y_true), np.array(y_pred)
  return np.mean(np.abs((y_true - y_pred) / np.maximum(np.ones(len(y_true)), np.abs(y_true))))*100


###############################################################
#               READ DATA FROM EXCEL FILE                     #
###############################################################                                       
#Load data set
data = pd.read_excel('excel_data/v6andv7.xlsx',index_col=False)

###############################################################
#             CREATE AND TRAIN PHYSICAL MODELS                #
###############################################################

#Only use physical input (v_i, length, a and delta)
X_p = data.drop(["pi1","pi2","pi3","pi4","pi5","pi6","pi7","pi8","pi9","pi10","pi11","X","Y","theta"],axis=1)
X_p = X_p.values

#Only use y as output
y_X_p = data["X"].values
y_Y_p = data["Y"].values
y_T_p = data["theta"].values

#Create models
model_X_p = XGBRegressor()
model_Y_p = XGBRegressor()
model_T_p = XGBRegressor()

#Split data
X_X_train, X_X_test, y_X_train, y_X_test = train_test_split(X_p, y_X_p, test_size=0.2, random_state=42)
X_Y_train, X_Y_test, y_Y_train, y_Y_test = train_test_split(X_p, y_Y_p, test_size=0.2, random_state=42)    
X_T_train, X_T_test, y_T_train, y_T_test = train_test_split(X_p, y_T_p, test_size=0.2, random_state=42)        

#Fit models
model_X_p.fit(X_X_train,y_X_train)
model_Y_p.fit(X_Y_train,y_Y_train)
model_T_p.fit(X_T_train,y_T_train)

#Predict
y_X_pred = model_X_p.predict(X_X_test)
y_Y_pred = model_Y_p.predict(X_Y_test)
y_T_pred = model_T_p.predict(X_T_test)

# creating dataframe
df = pd.DataFrame({
    'Features': ["v_i", "l", "mu", "a","delta","m","Nf","Nr"],
    'To predict X-position': model_X_p.feature_importances_,
    'To predict Y-position': model_Y_p.feature_importances_,
    'To predict yaw': model_T_p.feature_importances_
})
  
df.plot(x="Features", y=['To predict X-position', 'To predict Y-position','To predict yaw'], kind="bar")

###############################################################
#          CREATE AND TRAIN DIMENSIONLESS MODELS              #
###############################################################

#Only use physical input (v_i, length, a and delta)
X_a = data.drop(["v_i","l","mu","a","delta","pi1","pi2","pi3","X","Y","theta","m","N_f","N_r"],axis=1)
X_a = X_a.values



#Only use y as output
y_X_a = data["pi1"].values
y_Y_a = data["pi2"].values
y_T_a = data["pi3"].values


#Create models
model_X_a = XGBRegressor()
model_Y_a = XGBRegressor()
model_T_a = XGBRegressor()  

#Split data
X_X_train, X_X_test, y_X_train, y_X_test = train_test_split(X_a, y_X_a, test_size=0.2, random_state=42)
X_Y_train, X_Y_test, y_Y_train, y_Y_test = train_test_split(X_a, y_Y_a, test_size=0.2, random_state=42)    
X_T_train, X_T_test, y_T_train, y_T_test = train_test_split(X_a, y_T_a, test_size=0.2, random_state=42)        

#Fit models
model_X_a.fit(X_X_train,y_X_train)
model_Y_a.fit(X_Y_train,y_Y_train)
model_T_a.fit(X_T_train,y_T_train)

#Predict
y_X_pred = model_X_a.predict(X_X_test)
y_Y_pred = model_Y_a.predict(X_Y_test)
y_T_pred = model_T_a.predict(X_T_test)

# creating dataframe
df = pd.DataFrame({
    'Features': ["pi4 = a*l/v_i**2", "pi5 = delta", "pi6 = Nf/Nr", "pi7 = mu","pi8 = 9.81*l/v_i**2","pi9 = rien","pi10 = limite long.","pi11 = limite lat."],
    'To predict X-position': model_X_a.feature_importances_,
    'To predict Y-position': model_Y_a.feature_importances_,
    'To predict yaw': model_T_a.feature_importances_
})
  
df.plot(x="Features", y=['To predict X-position', 'To predict Y-position','To predict yaw'], kind="bar")
# feature importance
print(model_X_a.feature_importances_)


###############################################################
#          CREATE AND TRAIN DIMENSIONLESS MODELS   PI            #
###############################################################

#Only use physical input (v_i, length, a and delta)
X_a = data.drop(["v_i","l","mu","a","delta","pi1","pi2","pi3","X","Y","theta","m","N_f","N_r","pi10","pi11"],axis=1)
X_a = X_a.values



#Only use y as output
y_X_a = data["pi1"].values
y_Y_a = data["pi2"].values
y_T_a = data["pi3"].values


#Create models
model_X_a = XGBRegressor()
model_Y_a = XGBRegressor()
model_T_a = XGBRegressor()  

#Split data
X_X_train, X_X_test, y_X_train, y_X_test = train_test_split(X_a, y_X_a, test_size=0.2, random_state=42)
X_Y_train, X_Y_test, y_Y_train, y_Y_test = train_test_split(X_a, y_Y_a, test_size=0.2, random_state=42)    
X_T_train, X_T_test, y_T_train, y_T_test = train_test_split(X_a, y_T_a, test_size=0.2, random_state=42)        

#Fit models
model_X_a.fit(X_X_train,y_X_train)
model_Y_a.fit(X_Y_train,y_Y_train)
model_T_a.fit(X_T_train,y_T_train)

#Predict
y_X_pred = model_X_a.predict(X_X_test)
y_Y_pred = model_Y_a.predict(X_Y_test)
y_T_pred = model_T_a.predict(X_T_test)

# creating dataframe
df = pd.DataFrame({
    'Features': ["pi4 = a*l/v_i**2", "pi5 = delta", "pi6 = Nf/Nr", "pi7 = mu","pi8 = 9.81*l/v_i**2","pi9 = rien"],
    'To predict X-position': model_X_a.feature_importances_,
    'To predict Y-position': model_Y_a.feature_importances_,
    'To predict yaw': model_T_a.feature_importances_
})
  
df.plot(x="Features", y=['To predict X-position', 'To predict Y-position','To predict yaw'], kind="bar")

plt.show()























