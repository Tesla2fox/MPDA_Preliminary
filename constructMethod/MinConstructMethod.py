# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:40:54 2018

GGQ's method

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


OrderTupleClass = collections.namedtuple('OrderTupleClass',['robID','taskID','vaild','syn_order'])
OnTaskInfoClass = collections.namedtuple('OnTaskInfoClass',['vaild','time','rate'])
INF_NUM = sys.float_info.max
INF_INT_NUM = sys.maxsize


class MinConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(MinConstructMethod,self).__init__(instance)
        degFileDir = BaseDir + '//debug//'
        ins = self._instance.insFileName.split('benchmark\\')
        degFileName = degFileDir + 'deg_Min' + ins[1]
        self.deg = open(degFileName,'w')
        '''
        in order to reduce the calculation period
        '''        
        self.c_weight = 0
        self._allocatedLst = []
    @CalPeriod()
    def construct(self,weightNum = 11,cmpltReverse = False):
        '''        
        return a optimal solution
        '''
        weightLst = self._generateWeightLst(weightNum)
#        weightLst = [0.5]*11        
        self._opt_solution = sol.Solution(self._instance)        
        for  weight in weightLst:
            self._solution = sol.Solution(self._instance)
            self.c_weight = weight                        
#            self.constructUint()
            self.deg.write('weight = '+str(self.c_weight) +'\n')
            try:
                self.constructUint()
            except Exception as e:
                print(e)
                self.deg.write(str(e) + '\n')
                continue
            else:                            
                self._solution.evaluate()
                if self._solution.objective < self._opt_solution.objective:
                    self._opt_solution = self._solution
        vaild  = False
        if self._opt_solution.objective != INF_NUM:
            vaild = True
        else:
            self.deg.write('can not get a solution \n')
        self.deg.close()        
        return vaild,self._opt_solution

    def constructUint(self):
        self._initState()
        self._allocatedLst = []
        
        self.cmpltTask  = [False] * self._instance.robNum
        while False in self.cmpltTask:                
                orderLst = []
                self.__sortPrePeriod()
                for key in self.onRoadOrderDic:
                    onRoadOrder = self.onRoadOrderDic[key]
                    onTaskOrder = self.onTaskOrderDic[key]
                    syntheticalOrder = self.c_weight * onRoadOrder + (1-self.c_weight) * onTaskOrder
                    orderLst.append(OrderTupleClass(key[0],key[1],self.onTaskPeriodDic[key].vaild,syntheticalOrder))
                minUnit = min(orderLst, key = cmp_to_key(self.__cmpSynOrder))                
                self.deg.write(str(minUnit) + '\n')
                print(minUnit)
                self.deg.flush()
                self.deg.write('___\n')
                orderLst = sorted(orderLst, key = cmp_to_key(self.__cmpSynOrder))
                for orderTuple in orderLst:
                    key = (orderTuple.robID,orderTuple.taskID)
                    self.deg.write(str(key)+' syn_ord ' + str(orderTuple.syn_order) +' ordTask '+str(self.onTaskOrderDic[key]) +' ordRoad '+ str(self.onRoadOrderDic[key]) \
                                   +' '+str(self.onTaskPeriodDic[key])  + ' ' + str(self.onRoadPeriodDic[key])+'\n')
                
                self.deg.flush()                    
#                    for key in self.onTaskOrderDic:
#                    orderTupel.RobID
#                print(orderLst)                
                self.__updateSol(minUnit)
                self.saveRobotInfo()
                self.saveTaskInfo()
                
        print(self._solution)
        
#                
#            for key in 
    
    def _initState(self):
#        OrderTupleClass(1,2,3)
        self._taskLst = []
        self._robLst = []
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
        for i in range(self._instance.taskNum):
            task = Task()
            task.cState = self._instance.taskStateLst[i]
            task.initState = self._instance.taskStateLst[i]
            task.cRate = self._instance.taskRateLst[i]
            task.initRate  = self._instance.taskRateLst[i]
            task.threhod = self._instance.threhold
            task.cmpltTime = sys.float_info.max
            self._taskLst.append(task)

    def __sortPrePeriod(self):
        self.onRoadOrderDic = dict()
        self.onTaskOrderDic = dict()

        preOnRoadPeriodLst = []
        preOnTaskPeriodLst = []
        
        allInvaild = True
        for robID in range(self._instance.robNum):
            for taskID in range(self._instance.taskNum):
                if (robID,taskID) not in self._allocatedLst:
                    onRoadPeriod = self._calRob2TaskPeriod(robID,taskID)
                    unit = ((robID,taskID),onRoadPeriod)
                    if self._robLst[robID].leaveTime + onRoadPeriod > self._taskLst[taskID].cmpltTime:
                        '''
                        preArriveTime > task.cmpltTime 
                            continue
                        '''
                        continue
                    preOnRoadPeriodLst.append(unit)
                    onTaskPeriod = self._calRobOnTaskPeriod(onRoadPeriod,robID,taskID)
                    if allInvaild and  onTaskPeriod.vaild:
                        allInvaild = False
                    unit = ((robID,taskID),onTaskPeriod)
                    preOnTaskPeriodLst.append(unit)
        
        self.onRoadPeriodDic = {unit[0]: unit[1] for unit in preOnRoadPeriodLst}
        self.onRoadOrderDic = self.sort(preOnRoadPeriodLst,reverse = False)
        self.onTaskPeriodDic = {unit[0]: unit[1] for unit in preOnTaskPeriodLst}        
        self.onTaskOrderDic = self.sort(preOnTaskPeriodLst, keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                        ,reverse = False)
#        print(self.onTaskOrderDic)
#        print(self.onTaskPeriodDic)

        self.deg.write('################################\n')        
        for key in self.onTaskOrderDic:
            self.deg.write(str(key)+' '+str(self.onTaskOrderDic[key])\
                           +' '+str(self.onTaskPeriodDic[key]) + ' ' + str(self.onRoadPeriodDic[key])+'\n')
        self.deg.write('\n')
        self.deg.flush()
        if allInvaild:
            raise Exception('all is invaild')
#        print(self.onRoadPeriodDic)
#        print(self.onRoadOrderDic)

        
    def __sortPreOnRoadPeriod(self):
        '''
        onRoadDic is a order dict
        '''
        self.onRoadOrderDic = dict()
        preOnRoadPeriodLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                if (i,j) not in self._allocatedLst:
                    period = self._calRob2TaskPeriod(i,j)
                    unit = ((i,j),period)
                    preOnRoadPeriodLst.append(unit)
        self.onRoadPeriodDic = {unit[0]: unit[1] for unit in preOnRoadPeriodLst}
        self.onRoadOrderDic = self.sort(preOnRoadPeriodLst,reverse = False)
        print(self.onRoadPeriodDic)
        print(self.onRoadOrderDic)
    def __sortPrePeriodUnableTask(self,taskID):
        '''
        input taskID
        return onRoad and ontask period order for the unableTask        
        '''
        self.onRoadOrderUnableDic = dict()
        preOnRoadPeriodLst = []        
        self.onTaskOrderUnableDic = dict()
        preOnTaskPeriodLst = []
        for i in range(self._instance.robNum):
            if (i,taskID) not in self._allocatedLst:
                onRoadPeriod = self._calRob2TaskPeriod(i,taskID)
                unit = ((i,taskID),onRoadPeriod)
                preOnRoadPeriodLst.append(unit)
                onTaskPeriod = self._calRobOnTaskPeriod(onRoadPeriod,i,taskID) 
                unit = ((i,taskID),onTaskPeriod)
                preOnTaskPeriodLst.append(unit)                

        self.onRoadUnableDic = {unit[0]: unit[1] for unit in preOnRoadPeriodLst}
        self.onRoadOrderUnableDic = self.sort(preOnRoadPeriodLst,reverse = False)
        self.onTaskUnableDic = {unit[0]: unit[1] for unit in preOnTaskPeriodLst}        
        self.onTaskOrderUnableDic = self.sort(preOnTaskPeriodLst,reverse = False)
        
        
    def __sortPreOnTaskPeriod(self,reverse = False):
        '''
        onTaskDic is a order dict
        '''
        self.onTaskOrderDic = dict()
        preOnTaskPeriodLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                if (i,j) not in self._allocatedLst:
                    onTaskPeriod = self._calRobOnTaskPeriod(i,j) 
                    unit = ((i,j),onTaskPeriod)
                    preOnTaskPeriodLst.append(unit)
        self.onTaskPeriodDic = {unit[0]: unit[1] for unit in preOnTaskPeriodLst}        
        self.onTaskOrderDic = self.sort(preOnTaskPeriodLst,reverse = False)
        print(self.onTaskOrderDic)
        print(self.onTaskPeriodDic)
    def _calRobOnTaskPeriod(self,onRoadPeriod,robID,taskID):
#        onRoadPeriod = self.onRoadPeriodDic[(robID,taskID)]
        rob = self._robLst[robID]
        robAbi = rob.ability
        calTask = copy.deepcopy(self.taskLst[taskID])
        if calTask.changeRateTime > rob.leaveTime + onRoadPeriod:
            raise Exception('changeRateTime')
        vaild = calTask.calCurrentState(rob.leaveTime + onRoadPeriod)
        cRate = sys.float_info.max
        executePeriod = sys.float_info.max
        if vaild == True:
            calTask.cRate = calTask.cRate - robAbi
            if calTask.cRate >=0:
                executePeriod = sys.float_info.max
            else:
                executePeriod = calTask.calExecuteDur()
            cRate = calTask.cRate
        return OnTaskInfoClass(vaild,executePeriod,cRate)
#        return     
    def _calRob2TaskPeriod(self,robID,taskID):
        '''
        calculate from the robot's position to the task's position.
        '''
        rob = self._robLst[robID]
        if rob.taskID == sys.maxsize:
            period = self._instance.calRob2TaskPeriod(robID,taskID)
        else:
            period = self._instance.calTask2TaskPeriod(robID,rob.taskID,taskID)
        return period
#            period = self.
#        rob.taskID = 
    def __sortPreFirstArrTime(self):
        self.arrDic = dict()
        preFirstArrTimeLst = []
        for i in range(self._instance.robNum):
            for j in range(self._instance.taskNum):
                if (i,j) not in self._allocatedLst:                    
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
        print(preCmpltTupleLst)
        self.cmpltDic =  self.sort(preCmpltTupleLst,keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                   ,reverse = cmpltReverse)
#        print(preCompTupleLst)
        print(self.cmpltDic)
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
#    def __cmpSynOrder(self,a,b):
    def __cmpSynOrder(self,a,b):
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
    def __updateSol(self,orderUnit ):
        rob = self._robLst[orderUnit.robID]
        self._solution[(orderUnit.robID,rob.encodeIndex)] = orderUnit.taskID
        rob.taskID = orderUnit.taskID
        rob.stateType = RobotState.onTask
        rob.encodeIndex += 1
        rob.arriveTime  = rob.leaveTime + self.onRoadPeriodDic[(orderUnit.robID,orderUnit.taskID)]
        self._allocatedLst.append((orderUnit.robID,orderUnit.taskID))
        self.__realArriveEvent(orderUnit.robID,orderUnit.taskID)
        while self._taskLst[orderUnit.taskID].cmpltTime == sys.float_info.max:
            '''
            let some robots go that task point to make sure it can be completed
            '''
            onTaskRobIDLst = self.__onTaskRobID(orderUnit.taskID)
            
            if len(onTaskRobIDLst) == self._instance.robNum:
                print(self._taskLst[orderUnit.taskID].cmpltTime)
                print(self._taskLst[orderUnit.taskID].cRate)
                raise Exception('wtf')
            self.__sortPrePeriodUnableTask(orderUnit.taskID)
            '''
            how to select some robots to be a supplement of the task which can 
            not be completed.
            this part can be optimized            
            '''
#            for weight in weightLst:
            orderLst = []
            for key in self.onRoadOrderUnableDic:
                onRoadUnableOrder = self.onRoadOrderUnableDic[key]
                onTaskUnableOrder = self.onTaskOrderUnableDic[key]
                syn_order =  self.c_weight * onRoadUnableOrder + (1 - self.c_weight) * onTaskUnableOrder
                orderLst.append(OrderTupleClass(key[0],key[1],self.onTaskUnableDic[key].vaild,syn_order))
            minUnit = min(orderLst,key = cmp_to_key(self.__cmpSynOrder))
            complementRob = self._robLst[minUnit.robID]
            self._solution[(minUnit.robID,complementRob.encodeIndex)] = minUnit.taskID
            complementRob.taskID = minUnit.taskID
            complementRob.stateType = RobotState.onTask
            complementRob.encodeIndex += 1
            self._allocatedLst.append((minUnit.robID,minUnit.taskID))
            complementRob.arriveTime  = complementRob.leaveTime + self.onRoadUnableDic[(minUnit.robID,minUnit.taskID)]
            self.__realArriveEvent(minUnit.robID,minUnit.taskID)        
            print(self._solution)
        self.deg.write('taskID = ' + str(orderUnit.taskID) + '\n')
        self.deg.write('updateOver = ' + str(self._taskLst[orderUnit.taskID].cmpltTime) + '\n')
        print('updateOver',self._taskLst[orderUnit.taskID].cmpltTime)
        
        
        
    def __realArriveEvent(self,robID,taskID):
        rob = self._robLst[robID]
        task = self._taskLst[taskID]
        leaveTime = INF_NUM
#        rob.arriveTime
        self.deg.write('real rob = ' + str(robID) +' real task = ' + str(taskID) + '\n')
        if task.cmpltTime < rob.arriveTime:
            raise Exception('here is a bug')
        else:
            validStateBool = task.calCurrentState(rob.arriveTime)
            print('real robID = ',robID)
            print('real taskID = ',taskID)
            if not validStateBool:
#                rob.arriveTime 
                print('real robID = ',robID)
                print('real taskID = ',taskID)
                print(rob.arriveTime )
                raise Exception('inValidStateBool')
                
            task.cRate = task.cRate - rob.ability
            if task.cRate >= 0:
                task.cmpltTime = INF_NUM
                return
            else:
                rob.executeDur = task.calExecuteDur()
                rob.executeBool = False
                leaveTime  = rob.arriveTime + rob.executeDur
                coordLst = self.findCoordRobot(robID)
                for coordID in coordLst:
                    coordRob = self._robLst[coordID]
                    coordRob.leaveTime = leaveTime
                    coordRob.executeDur = coordRob.leaveTime - coordRob.arriveTime
            rob.leaveTime = leaveTime
            rob.stateType = RobotState['onTask']
            task.cmpltTime = leaveTime
        
    def findCoordRobot(self,robID):
        '''
        find robots which are corrdinated with the robot A
        '''
        coordLst = []
        rob = self._robLst[robID]
        taskID =  rob.taskID
        for i in range(self._instance.robNum):
            if i == robID:
                continue
#            crob = self.robotLst[i]
            if self._robLst[i].stateType == RobotState['onRoad']:
                continue
            if self._robLst[i].stopBool == True:
                continue
            if self._robLst[i].taskID == taskID:
                coordLst.append(i)
        return coordLst                      
#                    z
#                break
    def saveRobotInfo(self):
        '''
        save robot information into the deg files 
        '''
        self.deg.write('\n')
        for i in range(self._instance.robNum):
            lst = []
            lst.append(i)
            lst.append('arriveTime')
            lst.append(self._robLst[i].arriveTime)
            lst.append('leaveTime')
            lst.append(self._robLst[i].leaveTime)
            lst.append('state')
            lst.append(self._robLst[i].stateType)
            lst.append('taskID')
            lst.append(self._robLst[i].taskID)
            str_lst  = [str(x) for x in lst]
            robInfo = '  '
            robInfo = robInfo.join(str_lst)
            self.deg.write(robInfo+'\n')
        self.deg.write('\n')
        self.deg.flush()
    def saveTaskInfo(self):
        self.deg.write('\n')
        for i in range(self._instance.taskNum):
            self.deg.write(str(i)+' cmpltTime = ' + str(self._taskLst[i].cmpltTime) + '\n')
    def __onTaskRobID(self,taskID):
        onTaskRobIDLst = []
        for i in range(self._instance.robNum):
            if self._robLst[i].stateType == RobotState.onRoad:
                continue
            if self._robLst[i].stopBool == True:
                continue
            if self._robLst[i].taskID == taskID:
                onTaskRobIDLst.append(i)
        return onTaskRobIDLst            
    def __str__(self):
        return 'StaticConstructMethod\n' + str(self._solution)
    
if __name__ == '__main__':    
    insName = '8_9_CLUSTERED_RANDOMCLUSTERED_UNITARY_LVSCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = MinConstructMethod(pro)
    
    print(con.construct())
    
#    print(pro)
#    random.seed(2)
#    print(con.construct(cmpltReverse = True))
#    print(con.Gconstruct(cmpltReverse = True))