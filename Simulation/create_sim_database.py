import xlsxwriter
import numpy as np


# Create a new workbook
wb = xlsxwriter.Workbook('/sim_database/data.xlsx')
sheet = wb.add_worksheet('Sheet1')	
sheet.write(0,0,"v_i")
sheet.write(0,1,"l")
sheet.write(0,2,"mu")
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
sheet.write(0,20,"N_f")
sheet.write(0,21,"N_r")




m  = 23.34
l = 1570
z = 0
w = 0.4



slip_max = 0.02

#for i in range(1,4,1):
#    if i == 1:
#        cg = 0.5
#    if i == 2:
#        cg = 1.0
#    if i == 3:
#        cg = 1.5
for i in range(1,2,1):
    if i == 1:
        cg = 0.75
        
    # Compute rear and front normal forces    
    N_r = m/(cg+1)*9.81
    N_f = m*9.81-N_r
    
    b = N_f/(m*9.81)*l
    a = l-b
    Iz = 1.00/12.00*m*(w**2+l**2)
                       
    for k in range(1,4,1):
        if k == 1:
            mu = 0.2
        if k == 2:
            mu = 0.4
        if k == 3:
            mu = 0.9  
        for v_i in range(1,51,1):
            v_i = v_i/10.0
            for a_u in range(1,11,1):
                a_u = a_u*0.1*9.81
                for delta in range(0,11,1):
                    delta = float(delta)/10.0*45*np.pi/180
                    z+=1
                    v_x = v_i
                    v_y = 0.0
                    omegaR = v_x
                    dtheta = 0.0
                    X = 0.0
                    Y = 0.0
                    theta = 0.0
                    dt = 0.00001
                    print('%.0f/%.0f' % (z,3*50*10*11))
        
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
                    
                    pi1 = X/l
                    pi2 = Y/l
                    pi3 = theta
                    pi4 = a_u*l/v_i**2
                    pi5 = delta
                    pi6 = N_f/N_r
                    pi7 = mu
                    pi8 = 9.81*l/v_i**2
                    pi9 = 0.0
                    pi10 = 9.81*mu/((cg+1)*a_u)
		    if delta == 0:
			pi11 = 100000
		    else:
			pi11 = 9.81*mu*l/(v_i**2*np.tan(delta))

                   
                    
                    sheet.write(z,0,v_i)
                    sheet.write(z,1,l)
                    sheet.write(z,2,mu)
                    sheet.write(z,3,a_u)
                    sheet.write(z,4,delta)
                    sheet.write(z,5,pi1)
                    sheet.write(z,6,pi2)     
                    sheet.write(z,7,pi3) 
                    sheet.write(z,8,pi4)
                    sheet.write(z,9,pi5)
                    sheet.write(z,10,X)        
                    sheet.write(z,11,Y)        
                    sheet.write(z,12,theta)
                    sheet.write(z,13,pi6) 
                    sheet.write(z,14,pi7)
                    sheet.write(z,15,pi8) 
                    sheet.write(z,16,pi9) 
                    sheet.write(z,17,m)
                    sheet.write(z,18,pi10)
                    sheet.write(z,19,pi11) 
		    sheet.write(z,20,N_f)
		    sheet.write(z,21,N_r)

                    


wb.close()

        
        
        



