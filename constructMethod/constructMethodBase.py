# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:02:43 2018

@author: robot
"""

import os,sys
AbsolutePath = os.path.abspath(__file__)           
#将相对路径转换成绝对路径
SuperiorCatalogue = os.path.dirname(AbsolutePath)   
#相对路径的上级路径
BaseDir = os.path.dirname(SuperiorCatalogue)        
#在“SuperiorCatalogue”的基础上在脱掉一层路径，得到我们想要的路径。
if BaseDir in sys.path:
#    print('have been added')
    pass
else:
    sys.path.append(BaseDir)
    
    
import constructMethod.instance as ins
import constructMethod.solution as sol
from functools import wraps
from Decode.task import Task



from enum import Enum
import time
import copy


class EventTime(Enum):
    ARRIVETIME = 1
    COMPLETETIME = 2
    EXECUTEPERIOD = 3
    
class ConstructMethodBase(object):
    def __init__(self, instance):
        self._instance = instance
        self._solution = sol.Solution(self._instance)
        self.taskLst = []
        self.__initTaskStates()
#        print('0-sa')
#        print(self.__ins)
#        instance.
#        super(ConstructMethodBase,self).__init__(insFileName)
    def calRob2TaskPeriod(self,robID,taskID):
        dur = self._instance.calRob2TaskPeriod(robID,taskID)        
        return dur
    def calRobFirstTaskEventTime(self,robID,taskID,EventTimeType = EventTime['COMPLETETIME']):
        dur = self._instance.calRob2TaskPeriod(robID,taskID)
        robAbi = self._instance.robAbiLst[robID]
        calTask = copy.deepcopy(self.taskLst[taskID])
        vaild = calTask.calCurrentState(dur)
        cRate = sys.float_info.max
        cmpTime = sys.float_info.max
        if vaild == True:
#            print(calTask)
#            print(self.taskLst[taskID])
            calTask.cRate = calTask.cRate - robAbi
            if calTask.cRate >=0:
                cmpTime = sys.float_info.max
            else:
                executeDur = calTask.calExecuteDur()
                cmpTime = dur + executeDur
            cRate = calTask.cRate
        return vaild,cmpTime,cRate

    def calRobFirstTaskCmplt(self,robID,taskID):
        dur = self._instance.calRob2TaskPeriod(robID,taskID)
        robAbi = self._instance.robAbiLst[robID]
        calTask = copy.deepcopy(self.taskLst[taskID])
        vaild = calTask.calCurrentState(dur)
        cRate = sys.float_info.max
        cmpTime = sys.float_info.max
        if vaild == True:
#            print(calTask)
#            print(self.taskLst[taskID])
            calTask.cRate = calTask.cRate - robAbi
            if calTask.cRate >=0:
                cmpTime = sys.float_info.max
            else:
                executeDur = calTask.calExecuteDur()
                cmpTime = dur + executeDur
            cRate = calTask.cRate
        return vaild,cmpTime,cRate
#        task = dt.Task()
        
    def sort(self,lst = [], keyFunc = lambda x: x[1] , reverse = False):
        lst = sorted(lst,key = keyFunc, reverse = reverse)
#        print(lst)
        val = sys.float_info.min
        orderInd = -1
        dic = dict()
        for index,unit in enumerate(lst):
            if val == unit[1]:
                dic[unit[0]] = orderInd
            else:
                val = unit[1]
                orderInd = index
                dic[unit[0]] = orderInd        
        return dic
    def __initTaskStates(self):
        self.taskLst = []
        for i in range(self._instance.taskNum):
            task = Task()
            task.cState = self._instance.taskStateLst[i]
            task.initState = self._instance.taskStateLst[i]
            task.cRate = self._instance.taskRateLst[i]
            task.initRate  = self._instance.taskRateLst[i]
            task.threhod = self._instance.threhold
            task.cmpltTime = sys.float_info.max
            self.taskLst.append(task)
    def _generateWeightLst(self,weightNum = 10):
        lst = []
        weightUnit = 1/(weightNum -1)
        for i in range(weightNum):
            lst.append(weightUnit*i)
        return lst
            
    
    def getUnitValue(self,x):
        return x[1]
    def __str__(self):
        return 'ConsturctMethodBase\n' + str(self.__solution)


class CalPeriod(object):
    def __init__(self):
        pass
#    @warps(func)
    def __call__(self,func):
        @wraps(func)
        def wrapper(*args,**kwargs):
#            print("before func")
            start = time.clock()
            wrapper_result=func(*args,**kwargs)
            end = time.clock()
            print('CalPeriod = ', end -start)
#            print("after func")
            return wrapper_result
        return wrapper
        
        

    
if __name__ == '__main__':
    
    insName = 's100_3_4_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.dat'
    pro = ins.Instance(BaseDir + '//data\\' + insName)    
    con = ConstructMethodBase(pro)
    print(con._solution)
    dic = dict()
    dic[1] = 1090
    print(dic)
    print(EventTime['COMPLETETIME'])
#    print(pro)
    
#    constructName = 's100_5_10_max100_2.5_2.5_2.5_1.2_thre0.1_MPDAins.dat'    
#    con = ConstructMethodBase(BaseDir + '//data\\' + constructName)
#    print(con)
#    print('wtf')
        