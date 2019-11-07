# TolTEC-HWP

This version of the code is written for python 3.
csv files contain frequency dependent refelctivities, absorptivities and temperatures
csv files other than the hwp file must have columns Frequency, Absorption, Reflection, Temperature Reflected, Temperature Emitted
The hwp csv should have columns:
Frequency, Transmittance C, Reflection C, Absorption C, Transmittance L, Reflection L, Absorption L, Dph, 45d X-Pol, [5 empty columns], Temp emitted, Temp reflected (see model_V1.csv or model_V2.csv)

Functions to calculate the effective temperature through each optical element are contained in hwp_func.py

To do the calculation run hwp_analysis.py.  As it is set up by default, the program should output Figure 4 from the synchronous signal paper.  The program will also create two output csv files, one containing the effective temp at each wavelength, and another containing band average effective temperatures, average temperatures, fractional differences, and picowatt loading.

In hwp_analysis.py the file_list on line 9 can be changed to adjust optical properties for each file individually.
