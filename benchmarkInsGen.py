# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 16:21:32 2018

the benchmark constructed by the paper {
New Benchmark Instances for the Capacitated Vehicle Routing Problem
}
@author: robot
"""

from enum import Enum
#import enum


'''
CNETRAL means all robots are in point(500,500)
ECCENTRIC means all robots are in the corner (0,0) of the work space
RANDOM
CLUSTED 
SV = small value
LCV = large CV
'''
class POSDIS(Enum):
    CENTRAL = 0    
    ECCENTRIC = 1
    RANDOM = 2
    CLUSTERED = 3
    RANDOMCLUSTERED = 4
#    Eccentric 
    
class VALUEDIS(Enum):
    UNITARY = 0
    SVLCV = 1
    SVSCV = 2
    LVLCV = 3
    LVSCV = 4
    QUADRANT = 5
# many small values, few large values
    MSVFLV = 6


class Point(object):
    def __init__(self,x = 0,y = 0):
        self.x = x
        self.y = y
    def __eq__(self,other):
        if self.x==other.x and self.y==other.y:
            return True
        return False
    def __str__(self):
        return "x:"+str(self.x)+",y:"+str(self.y)


max_RobNum = 200
max_taskNum = 200
insNum = 2000

#for insInd in range(insNum):
    

    
if __name__ == '__main__':
    A = Point(3,3)
    B = Point(3,4)
    if A == B :
        print('wtf')
    print(A)
    print(POSDIS.RANDOMCLUSTERED)
#    print(VALUEDIS.__str__)
    wtf = list(enumerate(VALUEDIS))
    print(wtf)