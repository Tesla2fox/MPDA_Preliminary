# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 10:12:55 2018
this is a base DECODE CLASS for the MPDA problem

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




class InvalidStateException(Exception):
    '''
    Custom exception types about InvalidStateException
    '''
    def __init__(self):
        err = 'InvalidStateException'
        super(InvalidStateException,self).__init__(err)
#        Exception.__init__(self, err)

class RobotStuckException(Exception):
    '''
    Custom exception types about RobotStuckException
    '''
    def __init__(self):
        err = 'RobotStuckException'
        super(RobotStuckException,self).__init__(err)


from readCfg.read_cfg import Read_Cfg
import readCfg.read_cfg as rd
from Decode.task import *
import numpy as np
import random
from Decode.robot import *
from enum import Enum
import sys
from timeit import timeit
import time
import copy as cp 

#from memory_profiler import profile

class CalType(Enum):
    arriveCond = 1
    leaveCond = 2
    endCond = 3
    backCond = 4
    stateInvalidCond = 5
    
class DecodeBase:
    def __init__(self,insFileName):
        readCfg = Read_Cfg(insFileName)
        self.robNum = int(readCfg.getSingleVal('robNum')) 
        self.taskNum = int(readCfg.getSingleVal('taskNum'))
        self.threhold = readCfg.getSingleVal('comp_threhold')
        self.robAbiLst  = []
        self.robVelLst = []
        self.taskStateLst = []
        self.taskRateLst = []
        readCfg.get('rob_abi',self.robAbiLst)
        readCfg.get('rob_vel',self.robVelLst)
        readCfg.get('tsk_rat',self.taskRateLst)
        readCfg.get('tsk_state',self.taskStateLst)
        self.rob2taskDisMat = np.zeros((self.robNum,self.taskNum))
        disLst = []
        readCfg.get('rob2tskDis',disLst)
        for i in range(self.robNum):
            for j in range(self.taskNum):
                self.rob2taskDisMat[i][j] = disLst[i*self.taskNum+j]
                
        self.taskDisMat = np.zeros((self.taskNum,self.taskNum))
        disLst = []
        readCfg.get('tskDis',disLst)
        for i in range(self.taskNum):
            for j in range(self.taskNum):
                self.taskDisMat[i][j] = disLst[i*self.taskNum+j]

        self.encode = np.zeros((self.robNum,self.taskNum),dtype =int)
        self.taskLst = []
        self.robotLst = []
        self.cmpltLst = []
        self.decodeTime = 0        
        self.insFileName = insFileName        
        self.robInfoLst = []
        self.taskInfoLst = []
        self.decodeTimeLst = []
        
        self._degBool =  False        
    def generateRandEncode(self):
        for i in range(self.robNum):
            permLst = [x for x in range(self.taskNum)]
            random.shuffle(permLst)
            self.encode[i][:] = permLst
        
        
    def decode(self):
        '''
        ready to construct
        '''
        pass
    def initStates(self):
        '''
        initialize states of decode method 
        '''
        self.taskLst.clear()
        self.robotLst.clear()
        self.cmpltLst.clear()
        self.cmpltLst = [False] * self.taskNum
        for i in range(self.robNum):
            rob = Robot()
            rob.ability = self.robAbiLst[i]
            rob.vel = self.robVelLst[i]
            rob.encodeIndex = 0
            rob.taskID,rob.encodeIndex,stopBool = self.getRobTask(robID = i, encodeIndex = 0)
            if not stopBool:                
                dis  = self.rob2taskDisMat[i][rob.taskID]            
                dis_time = dis/rob.vel
                rob.arriveTime = dis_time
            rob.stopBool = stopBool
            rob.stateType = RobotState['onRoad']
            rob.leaveTime = 0
            self.robotLst.append(rob)
        
        for i in range(self.taskNum):
            task = Task()
            task.cState = self.taskStateLst[i]
            task.initState = self.taskStateLst[i]
            task.cRate = self.taskRateLst[i]
            task.initRate  = self.taskRateLst[i]
            task.threhod = self.threhold
            task.cmpltTime = sys.float_info.max
            self.taskLst.append(task)
            
        self.decodeTime = 0
        self.validStateBool = True
#    @profile
    def decodeProcessor(self):
        invalidFitness = False
        backBool = False
        validStateBool = True        
        while not self.allTaskCmplt():
            cal_type,actionID = self.findActionID()
            if cal_type  == CalType['arriveCond']:
# =============================================================================
# arrive event 
# =============================================================================

                rob = self.robotLst[actionID]
                arriveTime = rob.arriveTime
                encodeInd = rob.encodeIndex
                taskID = self.encode[actionID][encodeInd]
                if self.taskCmplt(taskID):
# =============================================================================
#  the task has been cmplt
# =============================================================================
                    self.arriveCmpltTask(actionID,encodeInd)
                else:
# =============================================================================
# the  task has not been cmplt
# =============================================================================                    
                    task = self.taskLst[taskID]
                    rob.taskID = taskID
                    validStateBool = task.calCurrentState(arriveTime)
                    if not validStateBool :
                        break
                    task.cRate = task.cRate - rob.ability
# can not be cmplted
                    if task.cRate >= 0:
                        leaveTime = sys.float_info.max
# can be completed
                    else:
                        rob.executeDur = task.calExecuteDur()
                        rob.executeBool = False
                        leaveTime = rob.arriveTime + rob.executeDur                        
                        coordLst = self.findCoordRobot(actionID)                        
                        for coordID in coordLst:
                            coordRob = self.robotLst[coordID]
                            coordRob.leaveTime = leaveTime
                            coordRob.executeDur = coordRob.leaveTime - coordRob.arriveTime
                    rob.leaveTime = leaveTime                    
                    rob.stateType = RobotState['onTask']
                    self.decodeTime = rob.arriveTime
# =============================================================================
#  begin the leave condition for 
# =============================================================================
            if cal_type == CalType['leaveCond']:
                rob = self.robotLst[actionID]
#                print(actionID)
                taskID = rob.taskID 
#                try:
#                    if  taskID < 0:
#                        raise Exception('taskID < 0')
#                except Exception as e:
#                    print(e)                
#                print(taskID)
                task = self.taskLst[taskID]
                if self.cmpltLst[taskID] == True:
                    self.leaveCmpltTask(actionID)                    
#                    print(self.cmpltLst)                    
#                    validStateBool = True
#                    while True:                        
#                        print('bug',taskID)
#                        return 
                else:
                    validStateBool = task.calCurrentState(rob.leaveTime)
                    if not validStateBool :
                        break
                    if(task.isCmplt()):
                        self.cmpltLst[taskID] = True
                        try: 
                            self.updateEncode(taskID)
                        except Exception as e:
                            print(e)
                        coordLst  = self.findCoordRobot(actionID)
                        for coordID in coordLst:
                            self.updateRobLeaveCond(coordID)
                            self.robotLst[coordID].cmpltTaskLst.append(taskID)
                    self.updateRobLeaveCond(actionID)
                    self.robotLst[actionID].cmpltTaskLst.append(taskID)
                    self.robotLst[actionID].cmpltTaskID = taskID
                if self._degBool:                    
                    self.deg.write('taskID '+ str(taskID) +' has been cmplt\n')
                    #                self.deg.write('leaveChanged\n')
                    self.saveRobotInfo()
                
                task.cmpltTime = rob.leaveTime
                self.decodeTime =  rob.leaveTime
#                print(taskID,' cmpltTime ', task.cmpltTime)
            if cal_type == CalType['endCond']:
                invalidFitness = True
#                raise Exception('end-Condition-bug, robots have been stuck')
                raise RobotStuckException()
                break
            if cal_type  == CalType['backCond']:
                backBool = True
                self.backRobID = actionID
                self.backTaskID = self.robotLst[actionID].taskID
                self.backArriveTime = self.robotLst[actionID].arriveTime
                self.backInfo = self.robotLst[actionID].variableInfo() 
                break                    
#                
#                    print(task.cRate)
#                    print(task.cRate)
# =============================================================================
#  the state is too big  the decode process is wrong
# =============================================================================
            if not validStateBool:
                break
#            print('circleTime = ', circleTime)
#            print('decodeTime = ', self.decodeTime)
#            circleTime += 1 
#            if circleTime > 3000:
#                break            
#            print(self.cmpltLst)
        
        if not validStateBool:
            cal_type = CalType['stateInvalidCond']
            self.validStateBool = False
#            raise Exception('stateInvalidCond-bug, the state is too enormous')
            raise InvalidStateException()            
#        print(cal_type)        
        return cal_type
#            break
                
    def allTaskCmplt(self):
        if False in self.cmpltLst:
            return False
        else:
            return True
    
    def findActionID(self):
        cal_type = CalType['endCond']
        actionID = -1
        minTime = sys.float_info.max        
        for i in range(self.robNum):
            rob = self.robotLst[i]
            if rob.stopBool != True:
                if rob.stateType == RobotState['onRoad']:
                    if rob.arriveTime < minTime:
                        minTime = rob.arriveTime
                        cal_type = CalType['arriveCond']
                        actionID = i
                if rob.stateType == RobotState['onTask']:
                    if rob.leaveTime < minTime:
                        minTime = rob.leaveTime
                        cal_type = CalType['leaveCond']
                        actionID = i

        self.saveEventInMemory()
        
        if minTime < self.decodeTime:
            cal_type = CalType['backCond']
#            print(minTime)
#            print(self.decodeTime)
#            taskID = self.robotLst[actionI].taskID
#        self.saveRobotInfo()
        return cal_type,actionID
    def findCoordRobot(self,robID):
        '''
        find robots which are corrdinated with the robot A
        '''
        coordLst = []
        rob = self.robotLst[robID]
        taskID =  rob.taskID
        for i in range(self.robNum):
            if i == robID:
                continue
#            crob = self.robotLst[i]
            if self.robotLst[i].stateType == RobotState['onRoad']:
                continue
            if self.robotLst[i].stopBool == True:
                continue
            if self.robotLst[i].taskID == taskID:
                coordLst.append(i)
        return coordLst                        
    def calRoadDur(self,taskID1,taskID2,robID):
        '''
        calculate the time fragment from the time when robID leaves the taskID1 to
        the time when rob arrives the taskID2
        '''
        dis = self.taskDisMat[taskID1][taskID2]
        rob = self.robotLst[robID]
        roadDur = dis/rob.vel
        return roadDur
    def updateEncode(self,cmpltTaskID):
        '''
        correct the encode,
        delete furture tasks which have been completed.
        '''
        for i in range(self.robNum):
            rob = self.robotLst[i]
            for j in range(rob.encodeIndex + 1, self.taskNum):
                if  self.encode[i][j] == cmpltTaskID:
                    self.encode[i][j] = -1
    def updateRobLeaveCond(self,robID):
        '''
        update robot's state when the leave event has been triggered.
        '''
        rob = self.robotLst[robID]
        preTaskID = rob.taskID
        while True:
            if rob.encodeIndex  == (self.taskNum  - 1):
                rob.stopBool = True
                break
            rob.encodeIndex  += 1
            taskID = self.encode[robID][rob.encodeIndex]
            if self.taskCmplt(taskID):
                continue
            else:
                roadDur = self.calRoadDur(preTaskID,taskID,robID)
                arriveTime  = rob.leaveTime + rob.roadDur
                if arriveTime > self.taskLst[taskID].cmpltTime:
                    self.encode[robID][rob.encodeIndex] = -1
                    print('optimal')                    
                    continue
                rob.roadDur = roadDur
                rob.taskID = taskID
                rob.arriveTime = rob.leaveTime + rob.roadDur
                rob.stateType = RobotState['onRoad']
                break
    def taskCmplt(self,taskID):
        '''
        taskID has been completed or not
        '''
        cmplt = False
        if taskID < 0:
            cmplt = True
        else:
            if self.cmpltLst[taskID]:
                cmplt = True
        return cmplt                    
    def getRobTask(self,robID = 0, encodeIndex = 0):
        '''
        get the robot next task ID
        '''
        stopBool = False
        while True:
            if encodeIndex == self.taskNum:
                stopBool = True
                break
            taskID = self.encode[robID][encodeIndex]
            if taskID < 0:
                encodeIndex += 1
                continue
            else:
                break                        
        return taskID,encodeIndex,stopBool
    def calMakespan(self):
# makespan for the MPDA problem        
        leaveTimeLst = [rob.leaveTime for rob in self.robotLst]
        makespan = max(leaveTimeLst)
        return makespan            
    def saveEncode(self):
        '''
        save encode information into the deg2 files 
        '''
        for i in range(self.robNum):
            lst = list(self.encode[i][:])
            rd.writeConf(self.deg2,str(i),lst)
        self.deg2.flush()
        
    def saveRobotInfo(self):
        '''
        save robot information into the deg files 
        '''
        self.deg.write('\n')
        for i in range(self.robNum):
            lst = []
            lst.append(i)
            lst.append('arriveTime')
            lst.append(self.robotLst[i].arriveTime)
            lst.append('leaveTime')
            lst.append(self.robotLst[i].leaveTime)
            lst.append('state')
            lst.append(self.robotLst[i].stateType)
            lst.append('taskID')
            lst.append(self.robotLst[i].taskID)
            str_lst  = [str(x) for x in lst]
            robInfo = '  '
            robInfo = robInfo.join(str_lst)
            self.deg.write(robInfo+'\n')
        self.deg.write('\n')
        self.deg.flush()
    def saveEventInMemory(self):        
        pass
    def leaveCmpltTask(self,actionID):
        pass
    def arriveCmpltTask(self,actionID,encodeInd):
        pass
    def genNoBacktrackEncode(self):
        '''
        generate the no-backtrack encode        
        '''
        encode = np.zeros((self.robNum,self.taskNum),dtype =int)
        for i  in range(self.robNum):
            ind = 0 
            for j in range(self.taskNum):
                if self.encode[i][j] != -1:
                    encode[i][ind] = self.encode[i][j]
                    ind += 1
        return encode 
    def endDeg(self):
        self.deg.close()
        self.deg2.close()
        
if __name__ =='__main__':
    print('0-0')