'''

Written by William Therrien, August 2020

'''

import rosbag, sys
import tf
import os #for file management make directory
import xlrd
import matplotlib.pyplot as plt
import random
import numpy as np

#def movingaveragefilter(order, data, kernel):
#    fil = []
#    numerator = []
#    data_filtered = []
#    linear = 0
#    quadratic = 0
#    exponential = 0
#    if (kernel == "linear"):
#        linear = 1
#    elif(kernel == "quadratic"):
#        quadratic = 1
#    elif(kernel == "exponential"):
#        exponential = 1
#    else:
#        print("no valid kernel chosen for the moving average filter. linear kernel set as default")
#        linear = 1
#    
#    m = 1
#    b = 0.001
#    sum_coefficients = 1e3
#    while (sum_coefficients > 1):
#        m = m-0.00001
#        for i in range(1,order+1):
#            print(i)
#            if linear == 1:
#                fil.append(m*i+b)
#        		
#            if quadratic == 1:
#                fil.append(m*i^2+b)
#
#            if exponential == 1:
#                fil.append(m*np.exp(i)+b)
# 
#        sum_coefficients = sum( fil )
#        print(sum_coefficients)
#
#    for i in range( order, np.size( data )+1):
#        for j in range(1,order+1):
#            numerator[i, j] = data[i+1-j]
#        data_filtered[i] = sum( numerator[i, :]*np.transpose(fil))
#    return data_filtered

def movingAverageFilter(numbers, window_size):


    moving_averages = []
    i = 0
    while i < len(numbers) - window_size + 1:

        this_window = numbers[i : i + window_size]
        window_average = sum(this_window) / window_size
        moving_averages.append(window_average)
        i += 1
    return moving_averages

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
X_fil_list = []
Y_fil_list = []
mu_list = []
vi_list = []
u_list = []
l_list = []
k = 1
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
            X.append(msg.pose.position.x)
            Y.append(msg.pose.position.y)
            quat = (msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w)
            theta.append(tf.transformations.euler_from_quaternion(quat)[2])

    #Filter position
    X_filtered = movingAverageFilter( X, 25)
    Y_filtered = movingAverageFilter( Y, 25)


    # Array for all bags and features
    X_list.append(X)
    Y_list.append(Y)
    X_fil_list.append(X_filtered)
    Y_fil_list.append(Y_filtered)
    mu_list.append(mu)
    vi_list.append(v_i)
    u_list.append(u)
    l_list.append(l)

    bag.close()

    plt.figure(k)
    plt.plot(X_list[k-1],Y_list[k-1],'-b',label='Original signal')
    plt.plot(X_fil_list[k-1],Y_fil_list[k-1],'-r',label='Filtered signal')
    plt.title('Comparaison des signaux pour le bag ' + str(bagNumber))
    plt.xlabel('X_position (m)')
    plt.ylabel('Y_position (m)')
    plt.legend()
    k += 1
#random_bagNumber = []
#for i in range(0,15):
#    random_bagNumber.append(random.randrange(1,360,1))   
#k = 1
#for i in random_bagNumber:

#    plt.figure(k)
#    plt.plot(X_list[i],Y_list[i],'-b',label='Original signal')
#    plt.plot(X_fil_list[i],Y_fil_list[i],'-r',label='Filtered signal')
#    plt.title('Comparaison des signaux pour le bag ' + str(i))
#    plt.xlabel('X_position (m)')
#    plt.ylabel('Y_position (m)')
#    plt.legend()
#    k += 1
    

plt.show()

print "Done reading all " + numberOfFiles + " bag files."

