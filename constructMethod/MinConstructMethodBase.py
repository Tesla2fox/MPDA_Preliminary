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
TaskInfoClass = collections.namedtuple('TaskInfoClass',['changeRateTime','cRate','robID','robAbi'])
'''
TaskInfoUpdateClass is used for __realArrive function to update the task information
'''
TaskInfoUpdateClass = collections.namedtuple('TaskInfoUpdateClass',['changeRateTime','cRate','cmpltTime','cState'])
INF_NUM = sys.float_info.max
INF_INT_NUM = sys.maxsize


'''
RobotState do not have any use in minConstructMethod
'''


class MinConstructMethodBase(ConstructMethodBase):
    def __init__(self, instance):
        super(MinConstructMethodBase,self).__init__(instance)
        degFileDir = BaseDir + '//debug//'
        ins = self._instance.insFileName.split('benchmark\\')
        degFileName = degFileDir + 'deg_Min' + ins[1]
        self.deg = open(degFileName,'w')
        
        '''
        in order to reduce the calculation period
        '''        
        self.c_weight = 0
        self._allocatedLst = []
        self._degBool = False
    @CalPeriod()
    def construct(self,weightNum = 11,cmpltReverse = False):
        '''        
        return a optimal solution
        '''
        weightLst = self._generateWeightLst(weightNum)
#        weightLst = [1]*11        
        self._opt_solution = sol.Solution(self._instance)        
        for  weight in weightLst:
            self._solution = sol.Solution(self._instance)
            self.c_weight = weight                        
            self.constructUint()
            try:
                pass
                self.constructUint()
            except Exception as e:
                print(e)
                self.deg.write(str(e) + '\n')
                continue
            else:
                makespan = self.__calMakespan()
                self._solution.objective = makespan                            
                if  self._degBool:
                    self._solution.evaluate()
                    self.deg.write('weight = '+str(self.c_weight) +'\n')
                    print('makespan = ',makespan)
                    print('realObjective = ', self._solution.objective)
                    cmpltTimeLst = [task.cmpltTime for task in self._taskLst]
                    realCmpltTimeLst = [self._instance.decode.taskLst[i].cmpltTime for i in range(self._instance.taskNum)]                
                    print(cmpltTimeLst)
                    print(realCmpltTimeLst)
                    self.deg.write('real decode \n')
                    for i in range(self._instance.taskNum):
                        self.deg.write( str(i) + ' cmpltTime = '  + str(self._instance.decode.taskLst[i].cmpltTime) + '\n')
                    self.deg.write('decode Encode ' + str(self._solution))
                    self.deg.flush()                
                    if abs(makespan -self._solution.objective) > 0.01:                    
                        raise Exception('the two makespans are not equal')
                if self._solution.objective < self._opt_solution.objective:
                    self._opt_solution = self._solution
#            break
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
        self.cmpltTask  = [False] * self._instance.taskNum
        while False in self.cmpltTask:                
                orderLst = []
                self._delDict = dict()
                self.roadOrderDic = dict()
                self.executeOrderDic = dict()
                self.sortOrder()
                if len(self.onRoadOrderDic) == 0:
                    continue
                for key in self.onRoadOrderDic:
                    roadOrder = self.roadOrderDic[key]                    
                    executeOrder = self.executeOrderDic[key]                    
                    syntheticalOrder = self.c_weight * roadOrder + (1-self.c_weight) * executeOrder
                    orderLst.append(OrderTupleClass(key[0],key[1],self.onTaskPeriodDic[key].vaild,syntheticalOrder))
                minUnit = min(orderLst, key = cmp_to_key(self._cmpSynOrder))
                if self._degBool:
                    self._saveOrderLst(orderLst)                                
                self._updateSol(minUnit)
                if  self._degBool:    
                    self.saveRobotInfo()
                    self.saveTaskInfo()
                    self.deg.write(str(self._solution)+'\n')
    def sortOrder(self):
        pass
    def _initState(self):
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
        self.__saveInitTaskState()
        self._taskInfoLst = [[] for x in range(self._instance.taskNum)]
        
    
    def __sortPrePeriod(self):
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
        self.onTaskOrderDic = self.sort(preOnTaskPeriodLst, keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                        ,reverse = False)
        
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
        self.__sortPrePeriod()
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
        self.onTaskOrderUnableDic = self.sort(preOnTaskPeriodLst,keyFunc = cmp_to_key(self.__cmpCmpltTime)\
                                              ,reverse = False)                
#        pass        
    def _calRobOnTaskPeriod(self,onRoadPeriod,robID,taskID):
        rob = self._robLst[robID]
        robAbi = rob.ability
        calTask = copy.deepcopy(self._taskLst[taskID])
        if calTask.changeRateTime > rob.leaveTime + onRoadPeriod:
            '''
            this part can be optimized.
            '''                
            calTask.recover(*self._taskInitInfo[taskID])
            taskInfo = copy.deepcopy(self._taskInfoLst[taskID])
            taskInfo.append(TaskInfoClass(robID = robID, changeRateTime = (rob.leaveTime + onRoadPeriod),cRate = 10, robAbi = rob.ability))
            taskInfo =  sorted(taskInfo,key = lambda x: x.changeRateTime)
            '''
            _taskInforLst is sorted by the arriveTime 
            '''
            delIndexLst = []            
            for i in range(len(taskInfo)):
                taskInfoUnit = taskInfo[i]
                if calTask.cmpltTime < taskInfoUnit.changeRateTime:                    
                    delIndexLst.append(taskInfoUnit)
                    continue
                calTask.calCurrentState(taskInfoUnit.changeRateTime)
                calTask.cRate = calTask.cRate - taskInfoUnit.robAbi
                if calTask.cRate >= 0:
                    executePeriod = INF_NUM
                    calTask.cmpltTime = INF_NUM
                else:
                    executePeriod = calTask.calExecuteDur()
                    calTask.cmpltTime = taskInfoUnit.changeRateTime + executePeriod                    
            executePeriod = calTask.cmpltTime - rob.leaveTime - onRoadPeriod 
            resTuple = OnTaskInfoClass(vaild = True, time = executePeriod , rate = calTask.cRate)            
            if len(delIndexLst):
                self._delDict[(robID,taskID)] = delIndexLst
#                print(self._delDict)
        else:
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
            resTuple = OnTaskInfoClass(vaild,executePeriod,cRate)
        self.taskVariableDic[(robID,taskID)] = calTask.variableInfo()        
        return resTuple
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
    def __cmpCmpltTime(self,a,b):
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
    '''
    compare the time or periods 
    which are related with the execute time 
    from smaller to larger
    the invalid is always largest
    '''
    def _cmpTaskTime(self,a,b):
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
    '''
    Reverse
    compare the time or periods 
    which are related with the execute time 
    from  larger to smaller
    the invalid is always largest
    '''
    def _cmpTaskTimeRe(self,a,b):
        if a[1] == b[1]:
            return 0
        if a[1][0]==b[1][0]:
            if a[1][1] == b[1][1]:
                return b[1][2] - a[1][2]
            else:
                return b[1][1] - a[1][1]  
        else:
            if a[1][0] == False:
                return 1
            else: 
                return -1    
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
        
    def _updateSol(self,orderUnit):
        '''
        this part need some change        
        '''
        task = self._taskLst[orderUnit.taskID]
#        if orderUnit.robID == 5 and orderUnit.taskID == 5:            
#            raise Exception('assda')
        if (orderUnit.robID,orderUnit.taskID) in self._delDict:
            delLst = self._delDict[(orderUnit.robID,orderUnit.taskID)]
            if self._degBool:                
                self.deg.write('del \n')
                self.deg.write('insertRobID = ' + str(orderUnit.robID) +' ')
                self.deg.write('insertTaskID = ' + str(orderUnit.taskID) +' \n')            
            for delUnit in delLst:
                robID = delUnit.robID
                rob = self._robLst[robID]
                rob.encodeIndex = rob.encodeIndex - 1
                self._solution[(robID,rob.encodeIndex)] = -1
#                print(self._taskInfoLst[orderUnit.taskID])                
                self._taskInfoLst[orderUnit.taskID].remove(delUnit)
                '''
                _taskInfoLst need delete some info
                '''
                if self._degBool:                    
                    print(rob,rob.encodeIndex)
                    self.deg.write('delRobID = '+ str(robID)+ ' ')
                    self.deg.write('delEncodeIndex = '+ str(rob.encodeIndex) + ' ')
                    self.deg.write('delTaskID = ' + str(rob.taskID)+ '\n')
                if orderUnit.taskID != rob.taskID:
                    raise Exception('afas')
                if rob.encodeIndex == 0:
                    rob.leaveTime = 0
                    rob.taskID = sys.maxsize
                else:
                    previousTaskID = self._solution.encode[robID][rob.encodeIndex -1 ]
                    previousTask = self._taskLst[previousTaskID]
                    rob.taskID = previousTaskID
                    rob.leaveTime = previousTask.cmpltTime                     
            if self._degBool:                
                self.deg.write(str(self._solution)+'\n')
                self.deg.flush()
        self.__realArriveEvent(orderUnit.robID,orderUnit.taskID)
        
        while task.cmpltTime == sys.float_info.max:
            '''
            let some robots go that task point 
            to make sure it can be completed
            '''
            onTaskRobIDLst = self.__onTaskRobID(orderUnit.taskID)            
            if len(onTaskRobIDLst) == self._instance.robNum:
#                print(self._taskLst[orderUnit.taskID].cmpltTime)
#                print(self._taskLst[orderUnit.taskID].cRate)
                raise Exception('wtf')
                
            minUnit = self._selectRobot2UnableTask(orderUnit.taskID)
            
            if (minUnit.robID,minUnit.taskID) in self._delDict:
                delLst = self._delDict[(minUnit.robID,minUnit.taskID)]
                if self._degBool:                
                    self.deg.write('del \n')
                    self.deg.write('insertRobID = ' + str(minUnit.robID) +' ')
                    self.deg.write('insertTaskID = ' + str(minUnit.taskID) +' \n')            
                for delUnit in delLst:
                    robID = delUnit.robID
                    rob = self._robLst[robID]
                    rob.encodeIndex = rob.encodeIndex - 1
                    self._solution[(robID,rob.encodeIndex)] = -1
    #                print(self._taskInfoLst[orderUnit.taskID])                
                    self._taskInfoLst[orderUnit.taskID].remove(delUnit)
                    '''
                    _taskInfoLst need delete some info
                    '''
                    if self._degBool:                    
                        print(rob,rob.encodeIndex)
                        self.deg.write('delRobID = '+ str(robID)+ ' ')
                        self.deg.write('delEncodeIndex = '+ str(rob.encodeIndex) + ' ')
                        self.deg.write('delTaskID = ' + str(rob.taskID)+ '\n')
                    if minUnit.taskID != rob.taskID:
                        raise Exception('afas')
                    if rob.encodeIndex == 0:
                        rob.leaveTime = 0
                        rob.taskID = sys.maxsize
                    else:
                        previousTaskID = self._solution.encode[robID][rob.encodeIndex -1 ]
                        previousTask = self._taskLst[previousTaskID]
                        rob.taskID = previousTaskID
                        rob.leaveTime = previousTask.cmpltTime                     

            '''
            this part need some change
            '''
            self.__realArriveEvent(minUnit.robID,minUnit.taskID) 
        if self._degBool:
            self.deg.write('taskID = ' + str(orderUnit.taskID) + '\n')
            self.deg.write('updateOver = ' + str(self._taskLst[orderUnit.taskID].cmpltTime) + '\n')
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
        pass    
    def __realArriveEvent(self,robID,taskID):
        
#        if robID == 5 and taskID == 5:            
#            raise Exception('assda')
        rob = self._robLst[robID]
        if rob.encodeIndex != 0:
            self.cmpltTask[rob.taskID] = True            
        rob.taskID = taskID
        self._solution[(robID,rob.encodeIndex)] = taskID
        rob.encodeIndex += 1
        onRoadPeriod = self.onRoadPeriodDic[(robID,taskID)]
        '''
        onTaskPeriod contains three attributes
        '''
        onTaskPeriod = self.onTaskPeriodDic[(robID,taskID)].time
        self._allocatedLst.append((robID,taskID))
        task = self._taskLst[taskID]
        rob.arriveTime = rob.leaveTime + onRoadPeriod        
        taskInfo = TaskInfoClass(robID = robID,robAbi = rob.ability,changeRateTime = rob.arriveTime, cRate = task.cRate)
        self._taskInfoLst[taskID].append(taskInfo)
        '''
        this part can be optimized
        '''        
        if self._degBool:
            self.deg.write('real rob = ' + str(robID) +' real task = ' + str(taskID) + '\n')        
            self.deg.write(str(self._taskInfoLst[taskID]) + '\n')
        
        task.recover(*self.taskVariableDic[robID,taskID])
        if task.cRate >= 0:
            task.cmpltTime = INF_NUM
            
        else:
            rob.executeDur = onTaskPeriod
            rob.executeBool = False
            leaveTime = rob.arriveTime + rob.executeDur
            task.cmpltTime = leaveTime
            coordLst = self.findCoordRobot(robID)
            for coordID in coordLst:
                coordRob = self._robLst[coordID]
                coordRob.leaveTime = leaveTime
                coordRob.executeDur = coordRob.leaveTime - coordRob.arriveTime                
        rob.leaveTime = task.cmpltTime
        if self._degBool:
            self.deg.write('taskID = ' + str(task)+'\n')
            self.deg.write(str(self._solution)+'\n')
            self.deg.flush()
        return         
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
            if self._robLst[i].stopBool == True:
                continue
            if self._robLst[i].taskID == taskID:
                coordLst.append(i)
        return coordLst                      
    def __onTaskRobID(self,taskID):
        '''
        find robots which are on TaskID task
        '''
        onTaskRobIDLst = []
        for i in range(self._instance.robNum):
#            if self._robLst[i].stateType == RobotState.onRoad:
#                continue
            if self._robLst[i].stopBool == True:
                continue
            if self._robLst[i].taskID == taskID:
                onTaskRobIDLst.append(i)
        return onTaskRobIDLst            
    def __str__(self):
        return 'MinConstructMethod\n' + str(self._solution)
    def __calMakespan(self):
        cmpltTimeLst = [task.cmpltTime for task in self._taskLst]
        return max(cmpltTimeLst)
    def __saveInitTaskState(self):
        '''
        save the initial task state
        '''
        self._taskInitInfo = []
        for task in self._taskLst:
            variableInfo = task.variableInfo()
            self._taskInitInfo.append(variableInfo)        
    '''
    save debug message function  
    '''
    def saveRobotInfo(self):
        '''
        save robot information into the deg files 
        '''
        self.deg.write('\n')
        for i in range(self._instance.robNum):
            lst = []
            lst.append('robID')
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
    def _saveOrderLst(self,orderLst):
        '''
        '''
        self.deg.write('___\n')
        orderLst = sorted(orderLst, key = cmp_to_key(self._cmpSynOrder))        
        for orderTuple in orderLst:
            key = (orderTuple.robID,orderTuple.taskID)
            self.deg.write(str(key)+' syn_ord ' + str(orderTuple.syn_order) +' ordTask '+str(self.onTaskOrderDic[key]) +' ordRoad '+ str(self.onRoadOrderDic[key]) \
                           +' '+str(self.onTaskPeriodDic[key])  + ' ' + str(self.onRoadPeriodDic[key])+'\n')                
            self.deg.flush()
    def _saveOnTaskOrderDic(self):
        self.deg.write('################################\n')        
        for key in self.onTaskOrderDic:
            self.deg.write(str(key)+' '+str(self.onTaskOrderDic[key])\
                           +' '+str(self.onTaskPeriodDic[key]) + ' ' + str(self.onRoadPeriodDic[key])+'\n')
        self.deg.write('\n')
        self.deg.flush()

            
if __name__ == '__main__':    
    insName = '8_9_RANDOM_CLUSTERED_MSVFLV_SVLCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = MinConstructMethodRT(pro)
    print()
#    con.
    print(con.construct())
    