# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 16:54:47 2018

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


from constructMethod.constructMethodBase import ConstructMethodBase,CalPeriod        
import constructMethod.instance as ins
import constructMethod.solution as sol
import random
import collections
from functools import cmp_to_key
import time 

INF_NUM = sys.float_info.max
INF_INT_NUM = sys.maxsize

#OnRoadClass = collections.namedtuple('OnRoadClass',['taskID','onRoadPeriod'])

OnTaskClass = collections.namedtuple('OnTaskClass',['vaild','cmpltTime','arrTime',\
                                                    'state','rate'])
    
OrderTupleClass = collections.namedtuple('OrderTupleClass',['taskID','vaild','syn_order'])


class OneStepConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(OneStepConstructMethod,self).__init__(instance)
    def construct(self,weightNum = 11,cmpltReverse = False):
        self._opt_solution = sol.Solution(self._instance)

        weightLst = self._generateWeightLst(weightNum)
        start = time.clock()
        for weight in weightLst:
            self._solution = sol.Solution(self._instance)
            self.c_weight = weight                        
            self.constructFirstStep()
            print(self._solution)
            break
        end = time.clock()
        self._methodPeriod = end - start
        vaild  = False
        if self._opt_solution.objective != INF_NUM:
            vaild = True

        return vaild,self._opt_solution
    def constructFirstStep(self):
        for robID in range(self._instance.robNum):
            preFirstArrTimeLst = []
            preFirstCmpltTimeLst = []
            robAbi =  self._instance.robAbiLst[robID]
            cRateLst = []
            cStateLst = []
            for taskID in range(self._instance.taskNum):
                peri = self.calRob2TaskPeriod(robID,taskID)
                preFirstArrTimeLst.append((taskID,peri)) 
                task = self.taskLst[taskID]
                state = sys.float_info.max
                cmpltTime = sys.float_info.max
                cState,vaild = task.preCalCurrentState(peri)
#                print(cState)
                cRate = task.cRate - robAbi
                cRateLst.append(cRate)
                cStateLst.append(cState)
                if vaild == True:
                    if cRate >= 0:
                        cmpltTime = sys.float_info.max
                    else:
                        executePeriod = task.preCalExecuteDur(cState,cRate)
                        cmpltTime = executePeriod + peri                                    
                cmpltTuple  = (taskID,OnTaskClass(vaild = vaild,cmpltTime = cmpltTime\
                                                  , arrTime = peri, state = cState, rate = cRate))
                preFirstCmpltTimeLst.append(cmpltTuple)
            self.max_cRate = max(cRateLst)
            self.max_cState = max(cStateLst)
            onRoadOrderDic = self.sort(preFirstArrTimeLst, keyFunc = lambda x: x[1])
            onTaskOrderDic = self.sort(preFirstCmpltTimeLst, keyFunc = cmp_to_key(self._cmpOnTasktime))
            print(preFirstCmpltTimeLst)
            print(onTaskOrderDic)
            orderLst = []
            for key,unit in preFirstCmpltTimeLst:
#                key = unit.taskID  
                roadOrder = onRoadOrderDic[key]                    
                executeOrder = onTaskOrderDic[key]                    
                syntheticalOrder = self.c_weight * roadOrder + (1-self.c_weight) * executeOrder                
#                orderLst.append()
                orderLst.append(OrderTupleClass(key,unit.vaild,syntheticalOrder))
            minUnit = min(orderLst, key = cmp_to_key(self._cmpSynOrder))
            self._solution[(robID,0)] = minUnit.taskID                        
#            break
        pass    
    def _cmpSynOrder(self,a,b):
        if a.vaild == b.vaild and a.syn_order == b.syn_order:
            return 0
        if a.vaild == b.vaild:
            if a.syn_order < b.syn_order:
                return -1
            else:
                return 1
        else:
            if a.vaild == False:
                return 1
            else:
                return -1
    def _cmpOnTasktime(self,a,b):
        if a[1] == b[1]:
            return 0
        if a[1].vaild == b[1].vaild:
            if a[1].cmpltTime  == b[1].cmpltTime:
                a_est_cmpltTime = a[1].state / self.max_cState * a[1].rate /self.max_cRate
                b_est_cmpltTime = b[1].state / self.max_cState * b[1].rate /self.max_cRate               
                return b_est_cmpltTime - a_est_cmpltTime 
            else:
                return b[1].cmpltTime - a[1].cmpltTime
            pass
        else:
            if a[1].vaild == False:
                return 1
            else:
                return 1
        
#        pass
    def _sortPreFirstArrTime(self):
        self.arrDic = dict()
        preFirstArrTimeLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                dur = self.calRob2TaskPeriod(i,j)
                arrUnit  = ((i,j),dur)
                preFirstArrTimeLst.append(arrUnit)
        self.arrDic = self.sort(preFirstArrTimeLst,reverse = False)
        
        
    def __sortPreFirstCmpltTime(self,cmpltReverse = False):
        self.cmpltDic = dict()
        preCmpltTupleLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                    CmpltUnit = self.calRobFirstTaskCmplt(i,j)
                    preCmpltTupleLst.append(((i,j),CmpltUnit))
        self.cmpltDic =  self.sort(preCmpltTupleLst,keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                   ,reverse = cmpltReverse)

#    def _calRobOnTaskPeriod(self,robID,taskID,arrTime):
#        '''
#        this function only can calculate the first step 
#        '''
        

if __name__ == '__main__':
    insName = '20_20_CLUSTERED_RANDOMCLUSTERED_SVLCV_LVSCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = OneStepConstructMethod(pro)
    print(con.construct())        
    