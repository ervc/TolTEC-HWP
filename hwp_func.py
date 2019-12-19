import csv
import numpy as np
from math import pi, exp


def antenna_temp(emiss,nu,T):
    if T == 0:
        T_ant = 0
    else:
        h = 6.626e-34 #m^2.kg/s
        k = 1.381e-23 #m^2.kg.s^-2.K^-1

        num = h*nu/k
        den = exp(h*nu/(k*T))-1
        T_ant = emiss*num/den

    return T_ant


#rflag and aflag tell the function whether to include reflectivities and absorptivities
#if rflag == 0, then all reflectivity values are considered to be zero, same for aflag
#if rflag == 1, then reflectivites are taken from optical element csv, same for aflag
#aflag has the option of aflag == -1, this sets only the hwp absorptivity to zero
def before_hwp(Tin,file,rflag,aflag):
    #make a new empty list for output temperatures
    Tout=[]
    
    #note this file assumes columns are in order
    #Frequency, Absorptivity, Reflectivity, T_reflected, T_absorbed
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            #skip header row
            if line_count == 0:
                line_count += 1
            else:
                #again, assuming correct order of columns.  Indices can be changed, but all files
                #should be consistent with ordering of columns
                nu=float(row[0])*1e9 #Hz
                a=float(row[1])
                r=float(row[2])
                if rflag == 0:
                    r = 0
                if aflag == 0:
                    a = 0
                t=1-a-r
                T_a = float(row[4])
                T_r = float(row[3])
                
                a_T_ant = antenna_temp(a,nu,T_a)
                r_T_ant = antenna_temp(r,nu,T_r)
                Temp = t*Tin[line_count-1]+a_T_ant+r_T_ant
                Tout.append(Temp)
                
                line_count+=1
    return(Tout)
##############################
####    end before_hwp()  ####
##############################

def during_hwp(Tin,file,rflag,aflag):
    Tout_perp=[]
    Tout_para=[]
    
    '''Right now this has been designed with the same file for which I digitized HWP absorptions
    so the first column is Frequency, then 8 columns of data, then columns 9 and 10 are
    average absorptions for the two axes (Here the C axis is 'perpendicular' and the L axis is 'parallel').
    Column 11 is the temperature the HWP emits at.'''
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            #skip header(s)
            if line_count < 2:
                line_count+=1
            #skip to freq=100
            elif int(row[0]) >= 100:
                nu = int(row[0])*1e9 #Hz
                a_perp=float(row[3])
                a_para=float(row[6])
                r_perp=float(row[2])
                r_para=float(row[5])

                if rflag == 0:
                    r_perp = 0
                    r_para = 0
                if aflag == 0 or aflag == -1:
                    a_perp = 0
                    a_para = 0

                t_perp=1-a_perp-r_perp
                t_para=1-a_para-r_para
                T_emit = float(row[14])
                T_r = float(row[15])
                
                a_perp_T_ant = antenna_temp(a_perp,nu,T_emit)
                a_para_T_ant = antenna_temp(a_para,nu,T_emit)
                r_perp_T_ant = antenna_temp(r_perp,nu,T_r)
                r_para_T_ant = antenna_temp(r_para,nu,T_r)
                #note we skipped line_count==0 so first temp is at line_count==2
                Temp_perp = t_perp*Tin[line_count-2]+a_perp_T_ant+r_perp_T_ant
                Temp_para = t_para*Tin[line_count-2]+a_para_T_ant+r_para_T_ant
                
                Tout_perp.append(Temp_perp)
                Tout_para.append(Temp_para)
                
                line_count+=1
    return(Tout_perp, Tout_para)
##############################
####    end during_hwp()  ####
##############################

#this is the same as the before_hwp function but is made to take in two Temperatures and output two Temperatures
def after_hwp(Tin_perp,Tin_para,file,rflag,aflag):
    Tout_perp=[]
    Tout_para=[]
    
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                nu = float(row[0])*1e9 #Hz
                a=float(row[1])
                r=float(row[2])
                if rflag == 0:
                    r = 0
                if aflag == 0:
                    a = 0
                t=1-a-r

                T_a = float(row[4])
                T_r = float(row[3])
                
                a_T_ant = antenna_temp(a,nu,T_a)
                r_T_ant = antenna_temp(r,nu,T_r)
                Temp_perp = t*Tin_perp[line_count-1]+a_T_ant+r_T_ant
                Temp_para = t*Tin_para[line_count-1]+a_T_ant+r_T_ant
                
                Tout_perp.append(Temp_perp)
                Tout_para.append(Temp_para)
                
                line_count+=1
    return(Tout_perp, Tout_para)
#############################
####    end after_hwp()  ####
#############################


def picowatt_calc(lower_nu, upper_nu, freq, T_A, FWHM):
    k = 1.38e-23
    c = 3e8
    A = pi*(25**2)
    
    nu = (upper_nu+lower_nu)/2
    d_nu = upper_nu-lower_nu
    
    if int(nu) != nu:
        nu += 0.5
    index = freq.index(nu)
    Temp = T_A[index]
    
    nu = nu*10**9
    d_nu = d_nu*10**9
    
    FWHM_rad = (FWHM/3600)*(pi/180)
    HWHM = FWHM_rad/2
    Omega = pi*HWHM**2

    I_num = 2*k*nu**2
    I_den = c**2
    
    W = (I_num/I_den)*Temp*d_nu*A*Omega
    pW = W*10**12
    pW = pW/2 #cut in half for polarization detectors
    
    return(pW)
#################################
####    end picowatt_calc()  ####
#################################

def hwp_analysis(file_list,hwp_file,rflag,aflag):  
    
    #loop through each file
    for file in file_list:
        #this if statement checks if the output is a list,  All the files before the HWP should
        #output a list of temperatures, after the HWP the output will be a tuple including
        #a temperature for the parallel axis and a temperature for the perpendicular axis

        #first create the T_eff list to be checked using LMT data
        if 'LMT' in file:
            f = open(file, 'r')
            data = f.readlines()
            T_eff=[]
            for line in data:
                elements=line.split()
                T_eff.append(float(elements[3]))
        elif type(T_eff) == list:
            #if file is not the hwp file
            if file != hwp_file:
                T_eff = before_hwp(T_eff, file,rflag,aflag)
            else:
                T_eff = during_hwp(T_eff, file,rflag,aflag)
                T_perp = T_eff[0]
                T_para = T_eff[1]
        #after the HWP T_eff is a tuple, so the code used needs to calculate twice.
        else:
            T_perp, T_para = after_hwp(T_perp, T_para, file,rflag,aflag)
    
    #create empty lists for the analysis of Temperature data once all the files are looped through
    T_diff = []
    T_avg = []
    differential = []
    for i in range(len(T_perp)):
        #calculates difference and average T at each frequency
        T_diff.append(T_perp[i] - T_para[i])
        T_avg.append((T_perp[i]+T_para[i])/2)
    
    for i in range(len(T_diff)):
        #finally, calculates the percent differential (difference/average)
        differential.append(T_diff[i]/T_avg[i])
        
    #make a list of frequencies
    frequency = [i for i in range(100,321,1)]
    
    
    #get band averages
    differential_low_list = [differential[i] for i in range(len(frequency)) if frequency[i] >= 128 and frequency[i] <= 170]
    differential_med_list = [differential[i] for i in range(len(frequency)) if frequency[i] >= 195 and frequency[i] <= 245]
    differential_high_list = [differential[i] for i in range(len(frequency)) if frequency[i] >= 245 and frequency[i] <= 310]
    
    diff_low_band = np.mean(differential_low_list)
    diff_med_band = np.mean(differential_med_list)
    diff_high_band = np.mean(differential_high_list)
    
    T_diff_low_list = [T_diff[i] for i in range(len(frequency)) if frequency[i] >= 128 and frequency[i] <= 170]
    T_diff_med_list = [T_diff[i] for i in range(len(frequency)) if frequency[i] >= 195 and frequency[i] <= 245]
    T_diff_high_list = [T_diff[i] for i in range(len(frequency)) if frequency[i] >= 245 and frequency[i] <= 310]
    
    T_diff_low_band = np.mean(T_diff_low_list)
    T_diff_med_band = np.mean(T_diff_med_list)
    T_diff_high_band = np.mean(T_diff_high_list)
    
    T_avg_low_list = [T_avg[i] for i in range(len(frequency)) if frequency[i] >= 128 and frequency[i] <= 170]
    T_avg_med_list = [T_avg[i] for i in range(len(frequency)) if frequency[i] >= 195 and frequency[i] <= 245]
    T_avg_high_list = [T_avg[i] for i in range(len(frequency)) if frequency[i] >= 245 and frequency[i] <= 310]
    
    T_avg_low_band = np.mean(T_avg_low_list)
    T_avg_med_band = np.mean(T_avg_med_list)
    T_avg_high_band = np.mean(T_avg_high_list)
    
    picowatt_low = picowatt_calc(128,170,frequency,T_avg,9.5)
    picowatt_med = picowatt_calc(195,245,frequency,T_avg,6.3)
    picowatt_high = picowatt_calc(245,310,frequency,T_avg,5)
    
    #write outputs to csv file
    with open('output.csv', 'w', newline='') as csvfile:
        write_file = csv.writer(csvfile, delimiter=',')
        row=0
        for i in range(len(differential)+1):
            if row==0:
                write_file.writerow(['Frequency (GHZ)','T_diff (K)','T_avg (K)','Percent difference'])
                row+=1
            else:
                write_file.writerow([frequency[i-1], T_diff[i-1],T_avg[i-1],differential[i-1]])
                row+=1
                
    with open('band_avg_out.csv', 'w', newline='') as csvfile:
        write_file = csv.writer(csvfile, delimiter=',')
        write_file.writerow(['Band','Frequency (GHz)','Delta T_band (K)','T_band_avg (K)','Percent difference (band avg)','Picowatt loading'])
        write_file.writerow(['Low','128-170',T_diff_low_band,T_avg_low_band,diff_low_band,picowatt_low])
        write_file.writerow(['Medium','195-245',T_diff_med_band,T_avg_med_band,diff_med_band,picowatt_med])
        write_file.writerow(['High','245-310',T_diff_high_band,T_avg_high_band,diff_high_band,picowatt_high])

    delta_t_band_list=[T_diff_low_band, T_diff_med_band, T_diff_high_band]
    t_band_avg_list = [T_avg_low_band, T_avg_med_band, T_avg_high_band]
    band_percent_list=[diff_low_band, diff_med_band, diff_high_band]
    picowatt_list = [picowatt_low, picowatt_med, picowatt_high] 
    
    
    #Returned values returned are in decimal form.  So a differential of .1 is 10%, not .1%.
    return([frequency, T_diff, T_avg, differential, delta_t_band_list,t_band_avg_list,
        band_percent_list,picowatt_list])
################################
####    end hwp_analysis()  ####
################################
