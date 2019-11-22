import csv
import matplotlib.pyplot as plt

from hwp_func import before_hwp, during_hwp, after_hwp
from hwp_func import picowatt_calc, hwp_analysis

#include any and all files here IN ORDER!
#file 0 should be the atmosphere, then primary/secondary mirrors, etc...
file_list = ['LMT_annual_25.out','mirrors.csv','warm_optics.csv','model_V1.csv','window.csv','cold_optics_v3.csv','detector.csv']

# except hwp_model_file, files should have the columns Frequency, Absorption, Reflection, T_reflected, T_absorbed
# The code assumes the first row in each csv is a header and data begins on line 2

#rflag and aflag tell the function whether to include reflectivities and absorptivities
#if rflag == 0, then all reflectivity values are considered to be zero, same for aflag
#if rflag == 1, then reflectivites are taken from optical element csv, same for aflag
#aflag has the option of aflag == -1, this sets only the hwp absorptivity to zero
rflag = 1
aflag = 1

freq, td, ta, dif, dtbl, tbal, bpl, pwl = hwp_analysis(file_list,rflag,aflag)

################################
####    PLOTS BEGIN HERE    ####
################################
#begin plots
plt.figure(1, figsize=(15,15))


#temperature difference subplot   
ax1 = plt.subplot(311)
plt.plot(freq, td)

plt.title(r'2$\Omega$ synchronous signal for TolTEC HWP', size='x-large')

ax1.text(150,10, '150 GHz\nBand', ha='center', size='large')
ax1.text(220,10, '220 GHz\nBand', ha='center', size='large')
ax1.text(280,10, '300 GHz\nBand', ha='center', size='large')

#this section marks off each band blue with vertical lines
xc = [128,170,195,245,246,310]
for i in range(len(xc)):
    plt.axvline(x=xc[i], color='0.25', linestyle='dashed')
        
plt.ylabel('Temperature\ndifference (K)')
plt.setp(ax1.get_xticklabels(), visible=False)
plt.xlim(100,320)
plt.grid(b=True)


#percent difference subplot
ax2 = plt.subplot(312)
plt.plot(freq, dif)

ax2.text(150,-0.35, '150 GHz\nBand', ha='center', size='large')
ax2.text(220,-0.35, '220 GHz\nBand', ha='center', size='large')
ax2.text(280,-0.35, '300 GHz\nBand', ha='center', size='large')

for i in range(len(xc)):
    plt.axvline(x=xc[i], color='0.25', linestyle='dashed')

plt.ylabel('Percent\ndifference')
plt.setp(ax2.get_xticklabels(), visible=False)
plt.xlim(100,320)
plt.grid(b=True)


#average temperature subplot
ax3=plt.subplot(313)
plt.plot(freq, ta)

ax3.text(150,49, '150 GHz\nBand', ha='center', size='large')
ax3.text(220,49, '220 GHz\nBand', ha='center', size='large')
ax3.text(280,49, '300 GHz\nBand', ha='center', size='large')

for i in range(len(xc)):
    plt.axvline(x=xc[i], color='0.25', linestyle='dashed')
        
plt.xlabel('Fequency (GHz)')
plt.ylabel('Average\nTemperature (K)')
plt.xlim(100,320)
plt.grid(b=True)

plt.savefig('outplot.png')

plt.show()
