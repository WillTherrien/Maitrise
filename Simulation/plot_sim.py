
import numpy as np
import matplotlib.pyplot as plt


v_i = 4.75
l = 1.5
mu = 0.9
m = 11.35
cg = 0.88
a_u = 0.3*9.81
delta = 0.23
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
dt = 0.000001



slip_x_f = 0.0
slip_x_r = 0.0
slip_a_f = 0.0
slip_a_r = 0.0
Fx_f = 0.0
Fx_r = 0.0
Fy_f = 0.0
Fy_r = 0.0
t = 0.0


vx_list = []
vy_list = []
omegaR_list = []
X_list = []
Y_list = []
theta_list = []
slipxf_list = []
slipxr_list = []
slipaf_list = []
slipar_list = []
Fxf_list = []
Fxr_list = []
Fyf_list = []
Fyr_list = []
t_list = []

vx_list.append(v_x)
vy_list.append(v_y)
omegaR_list.append(omegaR)
X_list.append(X)
Y_list.append(Y)
theta_list.append(theta)
slipxf_list.append(slip_x_f)
slipxr_list.append(slip_x_r)
slipaf_list.append(slip_a_f)
slipar_list.append(slip_a_r)
Fxf_list.append(Fx_f)
Fxr_list.append(Fx_r)
Fyf_list.append(Fy_f)
Fyr_list.append(Fy_r)
t_list.append(t)





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
    
    vx_list.append(v_x)
    vy_list.append(v_y)
    omegaR_list.append(omegaR)
    X_list.append(X)
    Y_list.append(Y)
    theta_list.append(theta)
    slipxf_list.append(slip_x_f)
    slipxr_list.append(slip_x_r)
    slipaf_list.append(slip_a_f)
    slipar_list.append(slip_a_r)
    Fxf_list.append(Fx_f)
    Fxr_list.append(Fx_r)
    Fyf_list.append(Fy_f)
    Fyr_list.append(Fy_r)
    t_list.append(t)
    t+=dt


plt.figure(1)


plt.plot(X_list,Y_list,'--r', label='SIMULATION ')
plt.title("Trajectoire SIMULATION \n Decel: "+str(a_u)+"m/s**2, Steering: "+str(delta)+"rad , Vitesse: "+str(v_i)+", Mu: "+str(mu))
plt.xlabel('X_position (m)')
plt.ylabel('Y_position (m)')
plt.axis("equal")
plt.legend()



fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)

fig.suptitle("FORCES")

ax1.plot(t_list, Fxf_list,  '--b',label="Sim")
ax1.set_ylabel('Longitudinal force front wheel (N)')
ax2.plot(t_list, Fxr_list,  '--r',label="Sim")
ax2.set_ylabel('Longitudinal force rear wheel (N)')
ax3.plot(t_list, Fyf_list,  '--g',label="Sim")
ax3.set_ylabel('Lateral force front wheel (N)')
ax4.plot(t_list,Fyr_list,  '--k',label="Sim")
ax4.set_ylabel('Lateral force rear wheel (N)')
ax4.set_xlabel('Time (s)')
ax1.legend(loc=1)
ax2.legend(loc=1)
ax3.legend(loc=1)
ax4.legend(loc=1)


fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)

fig.suptitle("Slip")

ax1.plot(t_list, slipxf_list,  '--b',label="Sim")
ax1.set_ylabel('Slip ratio front wheel (N)')
ax2.plot(t_list, slipxr_list,  '--r',label="Sim")
ax2.set_ylabel('Slip ratio rear wheel (N)')
ax3.plot(t_list, slipaf_list,  '--g',label="Sim")
ax3.set_ylabel('Slip angle front wheel (N)')
ax4.plot(t_list,slipar_list,  '--k',label="Sim")
ax4.set_ylabel('Slip angle rear wheel (N)')
ax4.set_xlabel('Time (s)')
ax1.legend(loc=1)
ax2.legend(loc=1)
ax3.legend(loc=1)
ax4.legend(loc=1)

fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)

fig.suptitle("Vitesse")

ax1.plot(t_list, vx_list,  '--b',label="Sim")
ax1.set_ylabel('Vitesse longitudinale (m/s)')
ax2.plot(t_list, vy_list,  '--r',label="Sim")
ax2.set_ylabel('Vitesse laterale (m/s)')

ax1.legend(loc=1)
ax2.legend(loc=1)



plt.show()

           
            


        
        
        



