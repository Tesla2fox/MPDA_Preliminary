# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 09:20:31 2018

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
from enum import Enum


CandTupleClass = collections.namedtuple('CandTupleClass'\
                                         ,['robID','taskID','sol','val'])
CmpltStateTupleClass = collections.namedtuple('CmpltStateTupleClass'\
                                         ,['cmpltTime','cRate','sol','val'])
RobTaskPair =  collections.namedtuple('RobTaskPair',['robID','taskID'])

INF_NUM = sys.float_info.max
INF_INT_NUM = sys.maxsize

class GrdTax(Enum):
    '''
    same task and the makespan which changes into a smaller value
    '''
    sTask_MS_C = 1
    '''
    more tasks and makespan without any changes    
    '''
    mTask_MS_UC = 2
    '''
    more tasks and makespan increased by a finite value
    or makespan changed into an infinite value
    '''
    mTask_MS_FSM = 3
    mTask_MS_INF = 4
    ''' 
    same tasks and the makespan without any changes but one task's cmpltTime decreases 
    same tasks and the makespan and all tasks' cmpltTime are same
    '''
    sTask_MS_UC_C = 5
    sTask_MS_UC_UC = 6       

                     
class GreedyConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(GreedyConstructMethod,self).__init__(instance)
        degFileDir = BaseDir + '//debug//'
        ins = self._instance.insFileName.split('benchmark\\')
        degFileName = degFileDir + 'deg_Greedy' + ins[1]
        self.deg = open(degFileName,'w')
    @CalPeriod()
    def construct(self):
        self._opt_solution = sol.Solution(self._instance)
        self._initState()
        while True:
            candLst = []                
            if self._grd_makespan == INF_NUM:
                for robID in range(self._instance.robNum):
                    unAllocateTaskLst = self._robUnAllocated[robID]
                    rob = self._robLst[robID]
                    if self._grd_pair.taskID in unAllocateTaskLst:
                        candidateSol = copy.deepcopy(self._opt_solution)
                        candidateSol[(robID,rob.encodeIndex)] = taskID
                        vaild,solVal = self._evaluateSol(candidateSol)                
                        if vaild:                        
                            candTuple = CandTupleClass(robID = robID, taskID = taskID, sol = candidateSol, val = solVal)
                            candLst.append(candTuple)
            else:
                for robID in range(self._instance.robNum):
                    unAllocateTaskLst = self._robUnAllocated[robID]
                    rob = self._robLst[robID]            
                    for taskID in unAllocateTaskLst:
                        candidateSol = copy.deepcopy(self._opt_solution)
                        candidateSol[(robID,rob.encodeIndex)] = taskID
                        vaild,solVal = self._evaluateSol(candidateSol)                
                        if vaild:                        
                            candTuple = CandTupleClass(robID = robID, taskID = taskID, sol = candidateSol, val = solVal)
                            candLst.append(candTuple)
            if len(candLst):                
                bestCand = min(candLst,key = lambda x: x.val)
                unAllocateTaskLst = self._robUnAllocated[bestCand.robID]
                unAllocateTaskLst.remove(bestCand.taskID)
                rob = self._robLst[bestCand.robID]
                rob.encodeIndex += 1            
                self._opt_solution = bestCand.sol
            else:
                break                
        return self._opt_solution
    def _evaluateSol(self,candidateSol):
        candidateSol.evaluate()
        print(candidateSol)
        cmpltLst = []
        for i in range(self._instance.taskNum):
            task = self._instance.decode.taskLst[i]
            if task.cRate < task.initRate:             
                cmpltLst.append(task.cmpltTime)
        print(cmpltLst)        
        candMakespan = max(cmpltLst)
        if candMakespan == sys.float_info.max:            
            raise Exception('fasd')        
        if random.random() > 0.8:
            return True,random.random()
        else:
            return False,random.random()            
    def _initState(self):
        self._robLst = []
        self._robUnAllocated = [[j for j in range(self._instance.taskNum)]\
                                for i in range(self._instance.robNum)]
        for i in range(self._instance.robNum):
            rob = Robot()
            rob.ability = self._instance.robAbiLst[i]
            rob.vel = self._instance.robVelLst[i]
            rob.encodeIndex = 0
            rob.taskID = sys.maxsize
            rob.arriveTime = sys.float_info.max
            rob.stateType = RobotState.onRoad
            rob.leaveTime = 0
            self._robLst.append(rob)
        self._grd_cmpltStateLst = []
        self._grd_makespan = 0
        self._grd_pair = RobTaskPair(robID = INF_INT_NUM,taskID = INF_INT_NUM)
        
        
    
if __name__ == '__main__':    
    insName = '8_9_RANDOM_CLUSTERED_MSVFLV_SVLCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = GreedyConstructMethod(pro)
    print(con.construct())     