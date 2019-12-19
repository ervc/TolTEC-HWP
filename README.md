# TolTEC-HWP

This version of the code is written for python 3.
csv files contain frequency dependent refelctivities, absorptivities and temperatures
csv files other than the hwp file must have columns Frequency, Absorption, Reflection, Temperature Reflected, Temperature Emitted
The hwp csv should have columns:
Frequency, Transmittance C, Reflection C, Absorption C, Transmittance L, Reflection L, Absorption L, Dph, 45d X-Pol, [5 empty columns], Temp emitted, Temp reflected (see model_V1.csv or model_V2.csv)

Functions to calculate the effective temperature through each optical element are contained in hwp_func.py


To do the calculation run 
$ python hwp_check.py [name of hwp file]

This code checks all of the assumptions listed in table 4 of the included paper (Modelling the 2-omega Synchronous Signal for the TolTEC Imaging Polarimeter.pdf). The output is a histogram (fig 5) and a modified version of fig 4 to include curves for each set of assumptions.

The Delta T threshold for each band can be adjusted in the hwp_check.py file on lines 14, 15, and 16 for the low, medium, and high bands respectively.
