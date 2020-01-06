import csv
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import os
import sys

from hwp_func import before_hwp, during_hwp, after_hwp
from hwp_func import hwp_analysis, picowatt_calc

##################################################

#Delta T temperature thresholds for the three bands in Kelvin
lowband_threshold = 1
medband_threshold = 0.8
highband_threshold = 0.5

##################################################

if len(sys.argv) == 1:
	print("hwp_file?\n")
	hwp_file = input()
elif len(sys.argv) == 2:
	hwp_file = sys.argv[1]
else:
	print('Error: input should be')
	print('$ python hwp_check [name of hwp file]')
	sys.exit()

if not os.path.exists(hwp_file):
	sys.exit('Error: Cannot find file: {}'.format(hwp_file))


print('hwp file is: ',hwp_file)
rflag = 1
aflag = 1

outfile = 'all_band_avg_out.csv'
failfile = 'all_band_avg_fails.csv'
outplot = 'all_hwp_outplot.png'
outhist = 'all_delta_t_histograms.png'
for filename in [outfile,failfile,outplot,outhist]:
	if os.path.exists(filename):
		print(filename+' already exists, removing it to create new file')
		os.remove(filename)
	else:
		print(filename+' does not already exist')

directory = 'input_files/'
atm_files = ['LMT_annual_5.out','LMT_annual_25.out','LMT_annual_50.out']
detect_files = ['detector_down.csv','detector.csv','detector_up.csv']
levels = ['down','mid','up']
co_files = []
for level_emis in levels:
	for level_temp in levels:
		co_file = 'cold_optics_'+level_emis+'_'+level_temp+'.csv'
		co_files.append(co_file)

with open(outfile,'a') as csvfile:
	file = csv.writer(csvfile,delimiter=',')
	file.writerow(['Band','Frequency','Delta_T band','T_band avg','Percent Difference','Picowatt Loading'])

print('Looping through assumptions...')
fig, (ax1,ax2,ax3) = plt.subplots(3,1, figsize=(10,9))

ax1.text(150,10, '150 GHz\nBand', ha='center', size='large')
ax1.text(220,10, '220 GHz\nBand', ha='center', size='large')
ax1.text(280,10, '300 GHz\nBand', ha='center', size='large')

ax2.text(150,-0.35, '150 GHz\nBand', ha='center', size='large')
ax2.text(220,-0.35, '220 GHz\nBand', ha='center', size='large')
ax2.text(280,-0.35, '300 GHz\nBand', ha='center', size='large')

ax3.text(150,49, '150 GHz\nBand', ha='center', size='large')
ax3.text(220,49, '220 GHz\nBand', ha='center', size='large')
ax3.text(280,49, '300 GHz\nBand', ha='center', size='large')

xc = [128,170,195,245,246,310]
for i in range(len(xc)):
	ax1.axvline(x=xc[i], color='0.25', linestyle='dashed')
	ax2.axvline(x=xc[i], color='0.25', linestyle='dashed')
	ax3.axvline(x=xc[i], color='0.25', linestyle='dashed')


for atm_file in atm_files:
	for co_file in co_files:
		for det_file in detect_files:
			for hwp_temp in [25, 45, 65]:
				filelist = [atm_file,'mirrors.csv','warm_optics.csv',hwp_file,'window.csv',co_file,det_file]
				filelist2 = [directory+f if f != hwp_file else f for f in filelist]

				freq,td,ta,dif,dtb,tba,bpl,pwl = hwp_analysis(filelist2,hwp_file,hwp_temp,rflag,aflag)

				with open(outfile,'a') as csvfile:
					writefile = csv.writer(csvfile, delimiter=',')
					writefile.writerow(filelist)
					writefile.writerow(['Low','128-170',dtb[0],tba[0],bpl[0],pwl[0]])
					writefile.writerow(['Medium','195-245',dtb[1],tba[1],bpl[1],pwl[1]])
					writefile.writerow(['High','245-310',dtb[2],tba[2],bpl[2],pwl[2]])
				with open(failfile,'a') as csvfail:
					fail_writer = csv.writer(csvfail,delimiter=',')
					if dtb[0]<(0-lowband_threshold) or dtb[0]>lowband_threshold:
						fail_writer.writerow(filelist)
						fail_writer.writerow(['Low','128-170',dtb[0],tba[0],bpl[0],pwl[0]])
					if dtb[1]<(0-medband_threshold) or dtb[1]>medband_threshold:
						fail_writer.writerow(filelist)
						fail_writer.writerow(['Medium','195-245',dtb[1],tba[1],bpl[1],pwl[1]])
					if dtb[2]<(0-highband_threshold) or dtb[2]>highband_threshold:
						fail_writer.writerow(filelist)
						fail_writer.writerow(['High','245-310',dtb[2],tba[2],bpl[2],pwl[2]])



				################################
				####    PLOTS BEGIN HERE    ####
				################################
				#begin plots

				#temperature difference subplot    
				
				ax1.plot(freq, td)

				ax1.set_title('All possible variations', size='x-large')

				ax1.set_ylabel('Temperature\ndifference (K)')
				plt.setp(ax1.get_xticklabels(), visible=False)
				ax1.set_xlim(100,320)
				ax1.grid(b=True)


				#percent difference subplot
				ax2.plot(freq, dif)

				ax2.set_ylabel('Fractional\ndifference')
				plt.setp(ax2.get_xticklabels(), visible=False)
				ax2.set_xlim(100,320)
				ax2.grid(b=True)


				#average temperature subplot
				ax3.plot(freq, ta)
						
				ax3.set_xlabel('Fequency (GHz)')
				ax3.set_ylabel('Average\nTemperature (K)')
				ax3.set_xlim(100,320)
				plt.grid(b=True)

print(outplot+' is done')
#optional savefig line
plt.savefig(outplot)
#cplt.show()
dt_all = []
delta_T = {'Low':['r'],'Medium': ['g'],'High': ['b']}
with open(outfile,'r') as file:
	reader = csv.reader(file)
	line = -1
	for row in reader:
		#skip header line
		if line <= 0:
			line += 1
		#skip section headers
		elif line % 4 == 0:
			line += 1
		else:
			delta_T[row[0]].append(float(row[2]))
			dt_all.append(float(row[2]))
			line+=1
print('making the histogram')
dt_min = min(dt_all)
dt_max = max(dt_all)
print('dt_min,max as float = ',dt_min,dt_max)
dt_min_int = int(dt_min)
if dt_min_int > dt_min or dt_min_int==0:
	dt_min_int-=1
	dt_min=dt_min_int
else:
	dt_min = dt_min_int
dt_max_int = int(dt_max)
if dt_max_int < dt_max or dt_max_int==0:
	dt_max_int+=1
	dt_max = dt_max_int
else:
	dt_max = dt_max_int
plt.figure()
print('dt_min,max integers = ',dt_min,dt_max)
bins = np.linspace(dt_min,dt_max,(dt_max-dt_min)*2+1)
print('bins = ',bins)
n_max=100 #set n_max at least 100 (purely for graphing)
for band in delta_T:
	print('working on %s band' % (band))
	n,bins,patches = plt.hist(delta_T[band][1:],bins,color=delta_T[band][0],alpha=0.25,label=band)
	print('For %s band, n is ' % (band))
	print(n)
	plt.hist(delta_T[band][1:],bins,color=delta_T[band][0],histtype='step',fill=False)
	if max(n) > n_max:
		n_max = max(n)
plt.legend()
if dt_min > -3:
	plt.xlim(left=-3)
if dt_max < 3:
	plt.xlim(right=3)
plt.xlabel('Temperature Difference (K)')
plt.ylabel('N',rotation=0)

plt.axvline(x=lowband_threshold,color=delta_T['Low'][0])
plt.axvline(x=(0-lowband_threshold),color=delta_T['Low'][0])
plt.axvline(x=medband_threshold,color=delta_T['Medium'][0])
plt.axvline(x=(0-medband_threshold),color=delta_T['Medium'][0])
plt.axvline(x=highband_threshold,color=delta_T['High'][0])
plt.axvline(x=(0-highband_threshold),color=delta_T['High'][0])

plt.title('Temperature difference for\nall hwp assumptions')

plt.savefig(outhist)
print('\nDONE: outputs are saved to {0}, {1}'.format(outplot, outhist))