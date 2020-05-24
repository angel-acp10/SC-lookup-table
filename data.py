'''
Lookup table generator (created by Angel Castro, tested under Python 3.7.3)
----------------------
@file: data.py

User parameters must be introduced through "data.py". To run the script execute
the file with "python3 lookup-ii.py". Parameters description is attached below:

    - _id: identifier which will be used to give names such as the lookup array
            or the files
    - _start_x: starting point of the lookup table
    - _end_x: final point of the lookup table. In fact, the real lookup table 
                might be a bit larger
    - _max_err: maximum desired absolute error 
    - _debug: Enables or disables the debug mode. (default: False)
    
The math equation is introduced through the function def equation(x)
'''

import math as m

class parameters:
    def __init__(self):
        self._id = 'sin'
        self._start_x = 0
        self._end_x = 1000
        self._max_err = 70
        self._debug = False

def equation(x):
    y = 1000*(1 + m.sin(2*m.pi*x/1000)-1)
    return y
