''' 
Lookup table generator (created by Angel Castro, tested under Python 3.7.3)
----------------------
@file: lookup-ii.py

Given a start, stop and maximum error, the script starts computing the 
minimum number of lookup points. The script will add points to the lookup 
table until the error is below the user specified threshold.

Once the solution is reached, the lookup table is written as a C program 
in the output folder. Finally, the solution is plotted, so the user can
visualize the results. 

User parameters must be introduced through "data.py". To run the script execute
this file with "python3 lookup-ii.py"
'''
#------------
# Libraries 
#------------
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

#-------------
# Input file 
#-------------
import data

#-------------
# Functions 
#-------------
#checks if a number is a power of two
def isPowerOfTwo(n):
    return not (n&(n-1))

#-------------
# Classes 
#-------------
#contains the lookup table data and functions to access to the data
class LookupTable:
    #dummy initializations
    _x = np.zeros(1) 
    _y = np.zeros(1)
    _x_seg_start = np.zeros(1)
    _x_seg_end = np.zeros(1)
    
    _dx = 0
    
    def __init__(self, start_x, stop_x, dx):

        self._dx = dx
        
        #x and y values of the lookup table
        self._x = np.arange(start_x, stop_x, dx)
        l = len(self._x)
        self._y = np.zeros(l)
    
        #"_x_seg_start" and "_x_seg_end" represent the corresponding x range
        #to each y value. "x" is in the middle of "_x_seg_start" and "_x_seg_end"
        self._x_seg_start = np.zeros(l)
        self._x_seg_end = np.zeros(l)
        
        for i in range(l):
            self._y[i] = int(data.equation(self._x[i]))
            self._x_seg_start[i] = self._x[i] - int(dx/2)
            self._x_seg_end[i] = self._x[i] + int(dx/2) - 1
            
            #first and last elements are shorter
            if i==0:
                self._x_seg_start[i] += int(dx/2)
            if i==l-1:
                self._x_seg_end[i] -= int(dx/2)
            
    #given a certain "x" value, computes the associated lookup table index 
    def getIndex(self, x):
        index = int( (x - (self._x[0] - self._dx/2))/self._dx )
        
        if index >= len(self._y):
            index = len(self._y)-1
        elif index < 0:
            index = 0
        
        return index
    
    #given a certain x value, returns its corresponding "y" lookup value
    def getY (self, x):
        index = self.getIndex(x)
        return self._y[index]
            
            
#-------------
# Main program
#-------------
#all the necessary parameters are introduced by the user through the "data.py" file
p = data.parameters()

#an initial dx seed is computed as follows
dx = int(p._end_x - p._start_x)

ite = 0

while True:
    
    ite += 1
    
    #if "dx" is a power of two, the computation of the lookup table index will be 
    #more efficient and therefore, we look for a power of two value
    while isPowerOfTwo(dx) == False:
        dx -= 1
    
    #compute the lookup array (this is the data that will be printed in the C file)
    lookup = LookupTable(p._start_x, p._end_x + dx, dx)
    if p._debug:
        print('\nThis is x_lookup, whose length is' + str(len(lookup._x_seg_start)))
        print(lookup._x_seg_start)
        print('\nThis is y_lookup, whose length is' + str(len(lookup._y)))
        print(lookup._y)
    
    #compute the float arrays (precise data)
    x_float = np.arange(p._start_x, p._end_x + dx/10, dx/10)
    l = len(x_float)
    y_float = np.zeros(l)
    for i in range(l):
        y_float[i] = data.equation(x_float[i])
    if p._debug:
        print('\nThis is x_float, whose length is' + str(len(x_float)))
        print(x_float)
        print('\nThis is y_float, whose length is' + str(len(y_float)))
        print(y_float)
    
    #compute the absolute error in function of x
    x_err = x_float
    l = len(x_err)
    y_err = np.zeros(l)
    for i in range(l):
        y_err[i] = lookup.getY(x_err[i]) - y_float[i]
    
    #check if the current error is acceptable and show information about the current iteration
    print('\n-----------------------------------------')
    print('ITE ' + str(ite) + ' dx = ' + str(dx) + ' nx = ' + str(len(lookup._y)) )
    max_err = np.nanmax( np.absolute(y_err) )
    
    if max_err <= p._max_err: #GOAL ACHIEVED, escape from while    
        print( '(error=' + str(max_err) + ') <= (usr_defined_err=' + str(p._max_err) + ') --> (GOAL ACHIEVED)' )
        break
    else: #GOAL FAILED
        print( '(error=' + str(max_err) + ') > (usr_defined_err=' + str(p._max_err) + ') --> (GOAL FAILED)' )
        #decrement dx and repeat the while
        dx = dx-1
        print('Trying with a higher number of points')
        if dx<1: #FATAL ERROR, escape from while
            print('ERROR: Impossible to get a higher resolution lookup table. Try with a lower accuracy.')
            break
        

#create the output directory
#---------------------------
dirName = "output/" + p._id + "/"
if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("Directory " + dirName +  " created")
else:    
    print("Directory " + dirName +  " already exists")


src_file = "lookup_" + p._id.lower() + ".c"
h_file = "lookup_" + p._id.lower() + ".h"

# output src_file 
#----------------
f = open(dirName + src_file, "w+")
f.write('#include "' + h_file + '"\r\n\r\n')

#choose the appropiate data type
array_type = "const"
minimum = np.nanmin(lookup._y) 
maximum = np.nanmax(lookup._y) 

if minimum >= 0: #unsigned type
    array_type += " uint"
    if maximum <= 2**8-1:
        array_type += "8_t"
    elif maximum <= 2**16-1:
        array_type += "16_t"
    elif maximum <= 2**32-1:
        array_type += "32_t"
    else:
        array_type += "64_t"
else: #signed type
    array_type += " int"
    if minimum>=-2**8/2 and maximum<=2**8/2-1:
        array_type += "8_t"
    elif minimum>=-2**16/2 and maximum<=2**16/2-1:
        array_type += "16_t"
    elif minimum>=-2**32/2 and maximum<=2**32/2-1:
        array_type += "32_t"
    else:
        array_type += "64_t"

#write the array
array_name = "lookup_" + p._id.lower()
f.write(array_type + " " + array_name + " [] = {\r\n")
for y, x, x_s, x_e in zip(lookup._y, lookup._x, lookup._x_seg_start, lookup._x_seg_end):
    f.write( "\t" + str(y) + ",\t// x @ " + str(x) + ", for range " + str(x_s) + " to " + str(x_e) + "\r\n")
f.write("};\r\n")
f.close()

# output h_file #
#----------------
f = open(dirName + h_file, "w+")
f.write('#include <stdint.h>\r\n\r\n')

def_start = "LU_" + p._id.upper()+ "_START"
f.write("#define " + def_start + " " + str(int(lookup._x_seg_start[0])) + "\r\n")

def_dx = "LU_" + p._id.upper() + "_DX"
f.write("#define " + def_dx + " " + str(int(dx)) + "\r\n")

def_half_dx = "LU_" + p._id.upper() + "_HALFDX"
f.write("#define " + def_half_dx + " " + str(int(dx/2)) + "\r\n")

def_log2_dx = "LU_" + p._id.upper() + "_LOG2DX"
f.write("#define " + def_log2_dx + " " + str(int(np.log2(dx))) + "\r\n")

def_get = "LU_GET_" + p._id.upper()
f.write("#define " + def_get + "(x) " + array_name + "[(x-(" + def_start + "-" + def_half_dx + "))>>" + def_log2_dx + "]\r\n\r\n")

f.write("extern " + array_type + " " + array_name + "[];\r\n")
f.close()

# Plot 
#------
fig, axs = plt.subplots(2, 1)

# Upper plot 
#------------
#draw all the discrete segments
for i in range(len(lookup._y)):
    x_line = [ lookup._x_seg_start[i], lookup._x_seg_end[i]+1]
    y_line = [ lookup._y[i], lookup._y[i] ]
    if i==0:
        axs[0].plot(x_line, y_line, c='r', linewidth=2.0, label='lookup')
    else:
        axs[0].plot(x_line, y_line, c='r', linewidth=2.0)

#draw the precise data
axs[0].plot(x_float, y_float, label='float')

legend = axs[0].legend()
axs[0].grid()

axs[0].set_title('N = ' + str(len(lookup._y)) + '   Dx = ' + str(dx)) 

# Lower plot 
#------------
axs[1].plot(x_err, y_err, c='r', label='err = lookup - float')
legend = axs[1].legend()
axs[1].grid()

plt.tight_layout()

# Save figure in multiple formats
#---------------------------------
fig_file = dirName + p._id
fig.savefig(fig_file + ".png")
fig.savefig(fig_file + ".pdf")
fig.savefig(fig_file + ".svg")
plt.show()











