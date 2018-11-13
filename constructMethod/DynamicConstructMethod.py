# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 20:23:58 2018

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
from functools import cmp_to_key
from Decode.robot import Robot,RobotState
from Decode.task import Task
import copy
import collections   
from constructMethod.MinConstructMethodBase import MinConstructMethodBase,OrderTupleClass



'''
onRoad and onTask
'''
class MinConstructMethodRT(MinConstructMethodBase):
    def __init__(self,instance):
        super(MinConstructMethodRT,self).__init__(instance)
        self.cmpTaskTime = self._cmpTaskTime
    def reverse(self,reverse = True):
        if reverse:
            self.cmpTaskTime = self._cmpTaskTimeRe
        else:
            self.cmpTaskTime = self._cmpTaskTime
    def sortOrder(self):
        self.onRoadOrderDic = dict()
        self.onTaskOrderDic = dict()

        preOnRoadPeriodLst = []
        preOnTaskPeriodLst = []
        
        allInvaild = True
        preCmpltTaskTime = [[] for i in range(self._instance.taskNum)]
        
        self.taskVariableDic = dict()        
        for robID in range(self._instance.robNum):
            for taskID in range(self._instance.taskNum):
                if self.cmpltTask[taskID]:
                    continue
                if (robID,taskID) not in self._allocatedLst:
                    onRoadPeriod = self._calRob2TaskPeriod(robID,taskID)
                    unit = ((robID,taskID),onRoadPeriod)
                    if self._robLst[robID].leaveTime + onRoadPeriod > self._taskLst[taskID].cmpltTime:
                        '''
                        preArriveTime > task.cmpltTime 
                            continue
                            this part still need process
                        '''
                        continue
                    preOnRoadPeriodLst.append(unit)
                    onTaskPeriod = self._calRobOnTaskPeriod(onRoadPeriod,robID,taskID)
                    if allInvaild and  onTaskPeriod.vaild:
                        allInvaild = False
                    unit = ((robID,taskID),onTaskPeriod)
                    preOnTaskPeriodLst.append(unit)
                    preCmpltTaskTime[taskID].append(self._robLst[robID].leaveTime + onRoadPeriod + onTaskPeriod.time)
                    
        self.onRoadPeriodDic = {unit[0]: unit[1] for unit in preOnRoadPeriodLst}
        self.onRoadOrderDic = self.sort(preOnRoadPeriodLst,reverse = False)
        self.onTaskPeriodDic = {unit[0]: unit[1] for unit in preOnTaskPeriodLst}        
        self.onTaskOrderDic = self.sort(preOnTaskPeriodLst, keyFunc = cmp_to_key(self.cmpTaskTime)\
                                        ,reverse = False)
        self.roadOrderDic = self.onRoadOrderDic
        self.executeOrderDic = self.onTaskOrderDic
        '''
        judge the task point has been completed or not
        '''        
        for taskID in range(len(self.cmpltTask)):
            if self.cmpltTask[taskID] == False:
                if len(preCmpltTaskTime[taskID]) == 0:
                    self.cmpltTask[taskID] = True
        if allInvaild and len(preOnRoadPeriodLst) != 0:
            raise Exception('all is invaild')    
    '''
    this function can be optimized.
    '''
    def _sortPrePeriodUnableTask(self,taskID):
        '''
        input taskID
        return onRoad and ontask period order for the unableTask        
        '''
        self.sortOrder()
#        self.__sortPrePeriod()
        if  self._degBool:
            self._saveOnTaskOrderDic()
        self.onRoadOrderUnableDic = dict()
        preOnRoadPeriodLst = []        
        self.onTaskOrderUnableDic = dict()
        preOnTaskPeriodLst = []        
        for i in range(self._instance.robNum):
            if (i,taskID) not in self._allocatedLst:
                onRoadPeriod = self.onRoadPeriodDic[(i,taskID)]
                unit = ((i,taskID),onRoadPeriod)
                preOnRoadPeriodLst.append(unit)
                onTaskPeriod = self.onTaskPeriodDic[(i,taskID)]
                unit = ((i,taskID),onTaskPeriod)
                preOnTaskPeriodLst.append(unit)
        self.onRoadUnableDic = {unit[0]: unit[1] for unit in preOnRoadPeriodLst}
        self.onRoadOrderUnableDic = self.sort(preOnRoadPeriodLst,reverse = False)
        self.onTaskUnableDic = {unit[0]: unit[1] for unit in preOnTaskPeriodLst}        
        self.onTaskOrderUnableDic = self.sort(preOnTaskPeriodLst,keyFunc = cmp_to_key(self.cmpTaskTime)\
                                              ,reverse = False)
    def _selectRobot2UnableTask(self,taskID):
        self._sortPrePeriodUnableTask(taskID)
        '''
        how to select some robots to be a supplement of the task which can 
        not be completed.
        this part can be optimized            
        '''
        orderLst = []
        for key in self.onRoadOrderUnableDic:
            onRoadUnableOrder = self.onRoadOrderUnableDic[key]
            onTaskUnableOrder = self.onTaskOrderUnableDic[key]
            syn_order =  self.c_weight * onRoadUnableOrder + (1 - self.c_weight) * onTaskUnableOrder
            orderLst.append(OrderTupleClass(key[0],key[1],self.onTaskUnableDic[key].vaild,syn_order))
        minUnit = min(orderLst,key = cmp_to_key(self._cmpSynOrder))
        return minUnit




       
if __name__ == '__main__':    
    insName = '26_26_CLUSTERED_ECCENTRIC_LVLCV_UNITARY_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = MinConstructMethodRT(pro)
#    print()
#    con.
#    print(con.construct())
#    con.reverse()
    print(con.construct())

#    pro.reverse()
#    pro = 