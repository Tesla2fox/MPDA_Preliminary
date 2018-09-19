# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 11:18:03 2018

inh is an abbreviation for inherent
@author: robot
"""

import numpy as np
import math
import sys

def getTaskDic():
    dic = dict()
    dic['initState'] = 0
    dic['init_rate'] = 0
# =============================================================================
# current state and rate 
# =============================================================================
    dic['c_state'] = 0
    dic['c_rate'] = 0
    dic['threhold'] = 0
    dic['cmplt'] = False
    return dic


class Task():
    def __init__(self):
        self.initState  = 0
        self.initRate = 0
        self.cState = 0
        self.cRate = 0
        self.changeRateTime = 0
        self.cmplt = False
        self.threhod = 0
        self.cmpltTime = 0
    def calExecuteDur(self):
#        print(self.threhod)
        e_dur = math.log(self.threhod/self.cState)/self.cRate
#        print(self.threhod)
#        print(self.cState)
        if e_dur <0:
            print('bug dur')
        return e_dur
# =============================================================================
# valid = false means that  cState is too high can not figure out
#   = true means that cState is right
# =============================================================================
    def calCurrentState(self,time):
        changeDur = time - self.changeRateTime
#        print(changeDur)
#        print(self.cState)
        incre = changeDur *self.cRate
        if incre > 709:
            return False         
        self.cState = self.cState*math.exp(changeDur*self.cRate)                
        valid =  True
        if(self.cState >sys.float_info.max ):
            valid = False
        self.changeRateTime = time
        return valid    
    def isCmplt(self):
#        print(self.cState)
#        print(self.threhod)
        bias = abs(self.cState - self.threhod)
        if bias < 0.000001:
            self.cmplt = True
            return True
        else:
            self.cmplt = False
            return False
    def display(self):
        print('initState',self.initState,' initRate',self.initRate,
              ' cState',self.cState,' cRate',self.cRate,
        ' changeRateTime',self.changeRateTime,' cmplt ',self.cmplt,
        ' threhod ',self.threhod)
    def variableInfo(self):
        return self.cState,self.cRate,self.changeRateTime,self.cmplt,self.cmpltTime
    def recover(self,cState,cRate,changeRateTime,cmplt,cmpltTime):
        self.cState = cState
        self.cRate = cRate
        self.changeRateTime = changeRateTime
        self.cmplt = cmplt
        self.cmpltTime = cmpltTime
if __name__ == '__main__':
    tsk = Task()
    tsk.display()
    print(tsk.initState)    
    print(math.log(1.7976931348623157e+308))
    