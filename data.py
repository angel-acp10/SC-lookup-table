import math as m

class parameters:
    def __init__(self):
        self._id = 'sin'
        self._start_x = 0
        self._end_x = 1000
        self._max_err = 10
        self._debug = False

def equation(x):
    y = 1000*(1 + m.sin(2*m.pi*x/1000)-1)
    return y
