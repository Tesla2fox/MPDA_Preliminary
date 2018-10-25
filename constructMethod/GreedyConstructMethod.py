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
                                         ,['robID','taskID','sol','solVal'])
CmpltStateTupleClass = collections.namedtuple('CmpltStateTupleClass'\
                                         ,['cmpltTime','cRate','sol','val'])
StateTuple = collections.namedtuple('StateTuple', ['grdType','makespan','cRate','cmpltRatio','cmpltState'])

RobTaskPair =  collections.namedtuple('RobTaskPair',['robID','taskID'])

CmpltStatePair = collections.namedtuple('CmpltStatePair',['cmpltTime','cRate','taskID'])

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
    
    InvalidState = 7

                     
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
                    taskID = self._grd_pair.taskID
                    if self._grd_pair.taskID in unAllocateTaskLst:
                        candidateSol = copy.deepcopy(self._opt_solution)
                        candidateSol[(robID,rob.encodeIndex)] = taskID
                        vaild,solVal = self._evaluateSol(candidateSol)                
                        if vaild:                        
                            candTuple = CandTupleClass(robID = robID, taskID = taskID, sol = candidateSol, solVal = solVal)
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
                            candTuple = CandTupleClass(robID = robID, taskID = taskID, sol = candidateSol, solVal = solVal)
                            candLst.append(candTuple)
            if len(candLst):                
                bestCand = min(candLst,key = cmp_to_key(self._cmpState))
                unAllocateTaskLst = self._robUnAllocated[bestCand.robID]
                unAllocateTaskLst.remove(bestCand.taskID)
                rob = self._robLst[bestCand.robID]
                rob.encodeIndex += 1            
                self._opt_solution = bestCand.sol
                print(bestCand.solVal.grdType)
                if len(self._grd_cmpltStateLst) == self._instance.taskNum:
                    if bestCand.solVal.grdType == GrdTax.sTask_MS_UC_C or bestCand.solVal.grdType == GrdTax.sTask_MS_UC_UC:
                        break
                self._grd_cmpltStateLst = bestCand.solVal.cmpltState
                self._grd_pair = RobTaskPair(robID = bestCand.robID, taskID = bestCand.taskID)
                self._grd_makespan = bestCand.solVal.makespan
#                raise Exception('sad')
                self.deg.write('_grd_pair = ' + str(self._grd_pair) + '\n')
                self.deg.write('_grd_makespan = ' + str(self._grd_makespan) + '\n')
                self.deg.write('solution = '+ str(self._opt_solution)+'\n')
                self.deg.write('ExecuteTaskNum = ' +str(len(self._grd_cmpltStateLst))+'\n')
                self.deg.flush()
            else:
                break                
        return self._opt_solution
    def _evaluateSol(self,candidateSol):
#        print(candidateSol)
        candidateSol.evaluate()
        grdType = GrdTax.InvalidState
        cmpltRatio = 0
        candMakespan = INF_NUM
        candCRate  = INF_NUM
        cmpltStateLst = []        
        if self._instance.decode.validStateBool:            
            for i in range(self._instance.taskNum):
                task = self._instance.decode.taskLst[i]
                if task.cRate < task.initRate:             
                    statePair = CmpltStatePair(cmpltTime = task.cmpltTime,cRate = task.cRate, taskID = i)
                    cmpltStateLst.append(statePair)            
#            print(cmpltStateLst)
            candState = max(cmpltStateLst, key = lambda x : x.cmpltTime)
            candMakespan = candState.cmpltTime
            candCRate = candState.cRate
            if len(self._grd_cmpltStateLst) > len(cmpltStateLst):
                print(self._grd_cmpltStateLst)
                print(cmpltStateLst)
                print(candidateSol)
                raise Exception('dada')
            grdType = self._tax(cmpltStateLst,candMakespan)
#        print(grdType)
#        print(candMakespan)
        
        if grdType == GrdTax.sTask_MS_UC_C or grdType == GrdTax.sTask_MS_C:
            grd_sum  = 0
            for unit in self._grd_cmpltStateLst:
                grd_sum += unit.cmpltTime
            cand_sum = 0
            for unit in cmpltStateLst:
                cand_sum += unit.cmpltTime
#            = sum(self._grd_cmpltStateLst, key = lambda x : x.cmpltTime)
#            cand_sum = sum(cmpltStateLst, key = lambda x : x.cmpltTime)
            cmpltRatio = (grd_sum - cand_sum) /grd_sum
#        StateTuple
        s_tuple = StateTuple(grdType = grdType, makespan = candMakespan, cRate = candCRate,\
                             cmpltRatio = cmpltRatio, cmpltState = cmpltStateLst)
        
        if grdType == GrdTax.InvalidState:
            return False,s_tuple
        else:
            return True,s_tuple
    def _tax(self,cmpltStateLst,makespan):
#        grdTaxRes
        if len(self._grd_cmpltStateLst) == len(cmpltStateLst):
            if self._grd_cmpltStateLst == cmpltStateLst:
                grdTaxRes = GrdTax.sTask_MS_UC_UC
            else:
                if makespan < self._grd_makespan:
                    grdTaxRes = GrdTax.sTask_MS_C
                else:
                    grdTaxRes = GrdTax.sTask_MS_UC_C
        else:
            if makespan == self._grd_makespan:
                grdTaxRes = GrdTax.mTask_MS_UC
            else:
                if makespan == INF_NUM:
                    grdTaxRes = GrdTax.mTask_MS_INF
                else:
                    grdTaxRes = GrdTax.mTask_MS_FSM
        return grdTaxRes
    def _cmpState(self,a,b):
        if a.solVal == b.solVal:
            return 0
        if a.solVal.grdType == b.solVal.grdType:
#            pass
            if a.solVal.grdType == GrdTax.InvalidState:
                return 0
            if a.solVal.grdType == GrdTax.sTask_MS_UC_UC:
                return a.solVal.cmpltRatio - b.solVal.cmpltRatio
            if a.solVal.grdType == GrdTax.sTask_MS_UC_C:
                return a.solVal.cmpltRatio - b.solVal.cmpltRatio
            if a.solVal.grdType == GrdTax.sTask_MS_C:
                return a.solVal.makespan - b.solVal.makespan
            if a.solVal.grdType == GrdTax.mTask_MS_INF:
                return a.solVal.cRate - b.solVal.cRate
            if a.solVal.grdType == GrdTax.mTask_MS_FSM:
                return a.solVal.makespan - b.solVal.makespan
            if a.solVal.grdType == GrdTax.mTask_MS_UC:      
                return a.solVal.cmpltRatio - b.solVal.cmpltRatio
        else:
            aVal = self.priDict[a.solVal.grdType]
            bVal = self.priDict[b.solVal.grdType]
            return aVal - bVal
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
        self._constructPriorityDict1()
    '''
    priDict1 
    '''        
    def _constructPriorityDict1(self):
        self.priDict = dict()
        self.priDict[GrdTax.InvalidState] = 7
        self.priDict[GrdTax.sTask_MS_UC_UC] = 6
        self.priDict[GrdTax.sTask_MS_UC_C] = 5
        self.priDict[GrdTax.sTask_MS_C] = 4
        self.priDict[GrdTax.mTask_MS_INF] = 3
        self.priDict[GrdTax.mTask_MS_FSM] = 2
        self.priDict[GrdTax.mTask_MS_UC] = 1
    '''
    priDict 2
    '''
    def _constructPriorityDict2(self):
        self.priDict = dict()
        self.priDict[GrdTax.InvalidState] = 7
        self.priDict[GrdTax.sTask_MS_UC_UC] = 6
        self.priDict[GrdTax.sTask_MS_UC_C] = 5
        self.priDict[GrdTax.mTask_MS_FSM] = 4
        self.priDict[GrdTax.mTask_MS_INF] = 3
        self.priDict[GrdTax.mTask_MS_UC] = 2
        self.priDict[GrdTax.sTask_MS_C] = 1
        
    '''
    deg msg function
    '''        
    def _saveCandLst(self,candLst):
        lst = sorted(candLst,key = cmp_to_key(self._cmpState))
        self.deg.write('______________\n\n')
        for unit in lst:
            self.deg.write('robID = '+ str(unit.robID) + ' taskID = '+ str (unit.taskID) + ' solVal = ' + str(unit.solVal)+'\n')
        self.deg.flush()
        
if __name__ == '__main__':    
    insName = '20_20_CLUSTERED_RANDOMCLUSTERED_SVLCV_LVSCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = GreedyConstructMethod(pro)
    print(con.construct())     