# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:40:54 2018

the zhu's method

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
from operator import itemgetter, attrgetter
from functools import cmp_to_key

class StaticConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(StaticConstructMethod,self).__init__(instance)
    @CalPeriod()
    def construct(self,weightNum = 11,cmpltReverse = False):
        '''
        zhu's method
        '''
        self._solution = sol.Solution(self._instance)
        self.__sortPreFirstArrTime()
        self.__sortPreFirstCmpltTime(cmpltReverse = cmpltReverse)        
        weightLst = self._generateWeightLst(weightNum)
#        print(weightLst)
        solSet = []
        for weight in  weightLst:
            orderLst = []
            for key in self.arrDic:
                arrOrder = self.arrDic[key]
                cmpltOrder = self.cmpltDic[key]
                syntheticalOrder = weight * arrOrder + (1-weight) * cmpltOrder
                orderLst.append((key,syntheticalOrder))
#            print(orderLst)
            orderLst = sorted(orderLst,key = lambda x : x[1])
            resSolution = self.__orderLst2Sol(orderLst)
            resSolution.evaluate()
            resSolution.genNoBackTrackEncode()
#            print(resSolution)
            if resSolution not in solSet:                
                solSet.append(resSolution)
            if resSolution.objective < self._solution.objective:
                self._solution = resSolution
#        print(len(solSet))
        return self._solution
    def Gconstruct(self,weightNum = 11,cmpltReverse = False):
        '''
        Gao's method
        '''
        self._solution = sol.Solution(self._instance)
        self.__sortPreFirstArrTime()
        self.__sortPreFirstCmpltTime(cmpltReverse = cmpltReverse)        
        weightLst = self._generateWeightLst(weightNum)
#        print(weightLst)
        solSet = []
        for weight in  weightLst:
            orderLst = []
            for key in self.arrDic:
                arrOrder = self.arrDic[key]
                cmpltOrder = self.cmpltDic[key]
                syntheticalOrder = weight * arrOrder + (1-weight) * cmpltOrder
                orderLst.append((key,syntheticalOrder))
#            print(orderLst)
            orderLst = sorted(orderLst,key = lambda x : x[1])
            resSolution = self.__orderLst2Sol(orderLst)
            resSolution.evaluate()
            resSolution.genNoBackTrackEncode()
#            print(resSolution)
            if resSolution not in solSet:                
                solSet.append(resSolution)
            if resSolution.objective < self._solution.objective:
                self._solution = resSolution
#        print(len(solSet))
        return self._solution    
    def __sortPreFirstArrTime(self):
        self.arrDic = dict()
        preFirstArrTimeLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                dur = self.calRob2TaskPeriod(i,j)
                arrUnit  = ((i,j),dur)
                preFirstArrTimeLst.append(arrUnit)
        self.arrDic = self.sort(preFirstArrTimeLst,reverse = False)
#        print(self.arrDic)
    def __sortPreFirstCmpltTime(self,cmpltReverse = False):
#        preFirstComTime = []
#        self.calRobFirstTaskComp(1,1)
        self.cmpltDic = dict()
        preCmpltTupleLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                    CmpltUnit =self.calRobFirstTaskCmplt(i,j)
#                    CmpltUnit =self.calRobFirstTaskCmplt(0,0)                                            
                    preCmpltTupleLst.append(((i,j),CmpltUnit))
#        preCompTupleLst[-1] = (((4,10),(False,199,1)))
        
#        print('begin _____ end')
#        print(preCmpltTupleLst)
        self.cmpltDic =  self.sort(preCmpltTupleLst,keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                   ,reverse = cmpltReverse)
#        print(preCompTupleLst)
#        print(self.cmpltDic)
#        print(preCompTupleLst)
    def __sortPreFirstExecuteTime(self,cmpltReverse = False):
#        preFirstComTime = []
#        self.calRobFirstTaskComp(1,1)
        self.executeDic = dict()
        preExecuteTupleLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                    executeUnit =self.calRobFirstTaskCmplt(i,j)
#                    if executeUnit                        
                    preCmpltTupleLst.append(((i,j),executeUnit))
#        preCompTupleLst[-1] = (((4,10),(False,199,1)))

#        print('begin _____ end')
        
        self.cmpltDic =  self.sort(preCmpltTupleLst,keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                   ,reverse = cmpltReverse)    
    def __cmpCmpltTime(self,a,b):
#        print('a = ',a)
#        print('b = ',b)
        if a[1] == b[1]:
            return 0
        if a[1][0]==b[1][0]:
            if a[1][1] == b[1][1]:
                return a[1][2] - b[1][2]
            else:
                return a[1][1] - b[1][1]
        else:
            if a[1][0] == False:
                return 1
            else: 
                return -1
    def __orderLst2Sol(self,orderLst = []):
        encodeIndLst = [0]*self._instance.robNum
        resSol = sol.Solution(self._instance)        
        for orderUnit in orderLst:
            robID = orderUnit[0][0]
            taskID = orderUnit[0][1]
#            resSol[]    
            resSol[(robID,encodeIndLst[robID])] = taskID
            encodeIndLst[robID] += 1
#        print(resSol)
        return resSol    
    def __str__(self):
        return 'StaticConstructMethod\n' + str(self._solution)
    
if __name__ == '__main__':    
    insName = '20_20_CLUSTERED_RANDOMCLUSTERED_SVLCV_LVSCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = StaticConstructMethod(pro)
#    print(pro)
#    random.seed(2)
    print(con.construct(cmpltReverse = True))
    print(con.construct(cmpltReverse = False))
    print(con.Gconstruct(cmpltReverse = True))