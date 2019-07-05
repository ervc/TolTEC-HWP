import csv
import matplotlib.pyplot as plt
import numpy as np
from math import pi

#include any and all files here IN ORDER!
#file 0 should be the outermost interface (light from the sky hits this thing first)
#then from file 0 light goes through file 1, then 2 then 3 etc.
file_list = ['mirrors.csv','warm_optics.csv','model_V1.csv','window.csv','cold_optics_v3.csv', 'detector.csv']

def before_hwp(Tin, file):
    #make a new empty list for output temperatures
    Tout=[]
    
    #note this file assumes columns are in order
    #Frequency, Absorption, Reflection, T_reflected, T_absorbed
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
                a=float(row[1])
                r=float(row[2])
                t=1-a-r
                T_a = float(row[4])
                T_r = float(row[3])
                
                Temp = t*Tin[line_count-1]+a*T_a+r*T_r
                Tout.append(Temp)
                
                line_count+=1
    return(Tout)

def during_hwp(Tin, file):
    Tout_perp=[]
    Tout_para=[]
    
    '''Right now this has been designed with the same file for which I digitized HWP absorptions
    so the first column is Frequency, then 8 columns of data, then columns 9 and 10 are
    average absorptions for the two axes (arbitrarily assigned parallel or perpendicular).
    Column 11 is the temperature the HWP emits at.  There is currently no reflection data so
    reflectivity is not included at all in the code, though it shouldn't be hard to add should
    that data be available.'''
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            #skip to freq=100
            if line_count < 92:
                line_count += 1
            else:
                a_perp=float(row[3])
                a_para=float(row[6])
                r_perp=float(row[2])
                r_para=float(row[5])
                t_perp=float(row[1])
                t_para=float(row[4])
                T_emit = float(row[14])
                T_r = float(row[15])
                
                
                Temp_perp = t_perp*Tin[line_count-92]+a_perp*T_emit+r_perp*T_r
                Temp_para = t_para*Tin[line_count-92]+a_para*T_emit+r_para*T_r
                
                Tout_perp.append(Temp_perp)
                Tout_para.append(Temp_para)
                
                line_count+=1
    return(Tout_perp, Tout_para)

#this is the same as the before_hwp function but is made to take in two Temperatures and output two Temperatures
def after_hwp(Tin_perp, Tin_para, file):
    Tout_perp=[]
    Tout_para=[]
    
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                a=float(row[1])
                r=float(row[2])
                t=1-a-r

                T_a = float(row[4])
                T_r = float(row[3])
                
                Temp_perp = t*Tin_perp[line_count-1] + a*T_a + r*T_r
                Temp_para = t*Tin_para[line_count-1] + a*T_a + r*T_r
                
                Tout_perp.append(Temp_perp)
                Tout_para.append(Temp_para)
                
                line_count+=1
    return(Tout_perp, Tout_para)

def picowattCalc(lower_nu, upper_nu, freq, T_A, FWHM):
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
    
    return(pW)

# note: [file_list] MUSt be csv files in order from sky to detector.  
# i.e file_list = ['mirrors.csv','warm_optics.csv','model_V1.csv','window.csv','cold_optics.csv']
# files except model_V1.csv should have the columns Frequency, Absorption, Reflection, T_reflected, T_absorbed
# The code assumes the first row in each csv is a header and data begins on line 2

def hwp_analysis(file_list):
    #start by making a list of "effective" sky temperatures for each frequency
    #Get antenna sky temp from am code
    file = open('LMT_annual_25.out', 'r')
    data = file.readlines()
    T_eff=[]
    for line in data:
        elements=line.split()
        T_eff.append(float(elements[3]))   
    
    #loop through each file
    for file in file_list:
        #this if statement checks if the output is a list,  All the files before the HWP should
        #output a list of temperatures, after the HWP the output will be a tuple including
        #a temperature for the parallel axis and a temperature for the perpendicular axis
        #T_eff_list = []
        if type(T_eff) == list:
            #if file is not the hwp file, this title can be changed if need be
            if file != 'model_V1.csv':
                T_eff = before_hwp(T_eff, file)
                #T_eff_list.append(T_eff[10])
            else:
                T_eff = during_hwp(T_eff, file)
                T_perp = T_eff[0]
                T_para = T_eff[1]
                #T_eff_list.append([T_perp[10], T_para[10]])
        #after the HWP T_eff is a tuple, so the code used needs to calculate twice.
        else:
            T_perp, T_para = after_hwp(T_perp, T_para, file)
            #T_eff_list.append([T_perp[10], T_para[10]])
    
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
    
    picowatt_low = picowattCalc(128,170,frequency,T_avg,9.5)
    picowatt_med = picowattCalc(195,245,frequency,T_avg,6.3)
    picowatt_high = picowattCalc(245,310,frequency,T_avg,5)
    
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
    
    #begin plots
    plt.figure(1, figsize=(15,20))
        
    ax1 = plt.subplot(311)
    plt.plot(frequency, T_diff, 'r-')
    
    ax1.text(150,10, '150 GHz\nBand', ha='center', size='xx-large')
    ax1.text(220,10, '220 GHz\nBand', ha='center', size='xx-large')
    ax1.text(280,10, '300 GHz\nBand', ha='center', size='xx-large')
    
    #plots lines at +/- 1K
    plt.axhline(1, c='k', linestyle='dashed')
    plt.axhline(-1, c='k', linestyle='dashed')
    
    #this section marks off each band blue for the low frequency, yellow for mid, green for high
    xc = [128,170,195,245,246,310]
    for i in range(len(xc)):
        plt.axvline(x=xc[i], color='0.25', linestyle='dashed')
            
    plt.ylabel('Temperature\ndifference (K)', size='large')
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.xlim(100,320)
    plt.grid(b=True)
    
    ax2 = plt.subplot(312)
    plt.plot(frequency, differential, 'r-')
    
    ax2.text(150,-0.35, '150 GHz\nBand', ha='center', size='xx-large')
    ax2.text(220,-0.35, '220 GHz\nBand', ha='center', size='xx-large')
    ax2.text(280,-0.35, '300 GHz\nBand', ha='center', size='xx-large')
    
    for i in range(len(xc)):
        plt.axvline(x=xc[i], color='0.25', linestyle='dashed')
    
    plt.ylabel('Percent\ndifference', size='large')
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.xlim(100,320)
    plt.grid(b=True)
    
    ax3 = plt.subplot(313)
    plt.plot(frequency, T_avg, 'r-')
    
    ax3.text(150,49, '150 GHz\nBand', ha='center', size='xx-large')
    ax3.text(220,49, '220 GHz\nBand', ha='center', size='xx-large')
    ax3.text(280,49, '300 GHz\nBand', ha='center', size='xx-large')
    
    for i in range(len(xc)):
        plt.axvline(x=xc[i], color='0.25', linestyle='dashed')
            
    plt.xlabel('Fequency (GHz)', size='x-large')
    plt.ylabel('Average\nTemperature (K)', size='large')
    plt.xlim(100,320)
    plt.grid(b=True)
    plt.text(0.5, -0.3, '2$\Omega$ synchronous signals for TolTEC\nas calculated by our code', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes, fontsize='24')
    
    #plt.tight_layout()
    
    plt.draw()
    
    #optional savefig line
    plt.savefig('hwp_analysis_results.png')
    
    #this is also optional, it's helpful if you want to look at actual numbers, just remember that
    #values returned are in decimal form.  So a differential of .1 is 10%, not .1%.
    return(frequency, T_diff, T_avg, differential, picowatt_low, picowatt_med, picowatt_high)

f, td, ta, dif, pico_low, pico_med, pico_high = hwp_analysis(file_list)
plt.show()
