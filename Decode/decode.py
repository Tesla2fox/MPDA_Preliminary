# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 10:12:55 2018

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
    print('have been added')
    pass
else:
    sys.path.append(BaseDir)

#sys.path.
#sys.path.insert(0,BaseDir)
print(sys.path)                          
#
##将我们取出来的路径加入到Python的命名空间去，并将该目录插入在第一个位置中。
#print(__file__)


from readCfg.read_cfg import Read_Cfg
import readCfg.read_cfg as rd
#from read_cfg import *
from Decode.task import *
#task import *
import numpy as np
import random
from Decode.robot import *
from enum import Enum
import sys
from timeit import timeit
import time

class CalType(Enum):
    arriveCond = 1
    leaveCond = 2
    endCond = 3
    backCond = 4
    stateInvalidCond = 5
    
class Decode:
    def __init__(self,insFileName):
        readCfg = Read_Cfg(insFileName)
#        ins_pic  = Pic()
        self.robNum = int(readCfg.getSingleVal('robNum')) 
        self.taskNum = int(readCfg.getSingleVal('tskNum'))
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
                self.rob2taskDisMat[i][j] = disLst[i*self.robNum+j]
                
        self.taskDisMat = np.zeros((self.taskNum,self.taskNum))
        disLst = []
        readCfg.get('tskDis',disLst)
        for i in range(self.taskNum):
            for j in range(self.taskNum):
                self.taskDisMat[i][j] = disLst[i*self.taskNum+j]

        self.encode = np.zeros((self.robNum,self.taskNum),dtype =int)

#        print(self.taskDisMat)
#        print(self.taskStateLst)
        self.taskLst = []
        self.robotLst = []
        self.cmpltLst = []
        self.decodeTime = 0        
        self.insFileName = insFileName
# =============================================================================
#  deg2 is for the decode process
# =============================================================================

        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data//')
        degFileName = degFileDir + 'deg_' + ins[1]
        self.deg = open(degFileName,'w') 
        
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data//')
        degFileName = degFileDir + 'deg2_' + ins[1]
        self.deg2 = open(degFileName,'w')        
        
    def generateRandEncode(self):
#        random.shuffle(permLst)
        for i in range(self.robNum):
#            for j in range(self.taskNum):
            permLst = [x for x in range(self.taskNum)]
            random.shuffle(permLst)
#            print(permLst)
            self.encode[i][:] = permLst
#        print(self.encode)
        
        
    def decode(self):
        circleTime = 0

        self.saveEncode()            

        while True:
            print('whileCircle = ',circleTime)
            circleTime += 1
            self.initStates()
            cal_type = self.decodeProcessor()
#            self.saveEncode()
            if cal_type == CalType['backCond']:
#                break
                continue
            else:
                break
#            print(self.cmpltLst)
        self.saveEncode()            

        if cal_type == CalType.stateInvalidCond:
#            print('invalidState')
            makespan = sys.float_info.max
        else:
#            print('validState')
            makespan = self.calMakespan()
        
#            pass
#            while True:
#                print('0-0')            
        return makespan
    def initStates(self):
        self.taskLst.clear()
        self.robotLst.clear()
        self.cmpltLst.clear()
        self.cmpltLst = [False] * self.taskNum
        for i in range(self.robNum):
            rob = Robot()
            rob.ability = self.robAbiLst[i]
            rob.vel = self.robVelLst[i]
            rob.encodeIndex = 0
            rob.taskID = self.encode[i][0]
            dis  = self.rob2taskDisMat[i][rob.taskID]            
            dis_time = dis/rob.vel
            rob.stateType = RobotState['onRoad']
            rob.arriveTime = dis_time
            rob.leaveTime = 0
            self.robotLst.append(rob)
        
        for i in range(self.taskNum):
            task = Task()
            task.cState = self.taskStateLst[i]
            task.initState = self.taskStateLst[i]
            task.cRate = self.taskRateLst[i]
            task.initRate  = self.taskRateLst[i]
            task.threhod = self.threhold
            self.taskLst.append(task)        
        self.decodeTime = 0
#        print(self.decodeTime)
#        for rob in self.robotLst:
#            rob.display()
#            print('__')
#        for task in self.taskLst:
#            task.display()
#            print('')
    def decodeProcessor(self):
        invalidFitness = False
        backBool = False
        validStateBool = True
        
        circleTime = 0
        while not self.allTaskCmplt():
            cal_type,actionID = self.findActionID()
#            self.deg.write('actionID  '+ str(actionID)+ '\n')
#            self.deg.write('cal_type  '+ str(cal_type) + '\n')
#            self.deg.flush()
            if cal_type  == CalType['arriveCond']:
                rob = self.robotLst[actionID]
                arriveTime = rob.arriveTime
#                taskID = rob.taskID
                encodeInd = rob.encodeIndex
                taskID = self.encode[actionID][encodeInd]
# =============================================================================
#  the task has been cmplt
# =============================================================================
                if(self.cmpltLst[taskID]):
#                   print(self.encode[actionID])
                   for i in range(encodeInd,self.taskNum - 1):
                       self.encode[actionID][i] = self.encode[actionID][i + 1]
                   self.encode[actionID][self.taskNum - 1] = taskID
#                   self.deg.write('pre_actionID = '+ str(actionID)+ '\n')
#                   self.deg.write('ecodeInd = '+ str(encodeInd) + '\n')
#                   self.deg.write('new_actionID = '+ str(self.encode[actionID][encodeInd]))
#                   print('taskID',taskID)
#                   print('encodeInd', encodeInd)
                   if encodeInd == 0:
                       taskID = self.encode[actionID][0]
                       dis  = self.rob2taskDisMat[actionID][rob.taskID]            
                       dis_time = dis/rob.vel
                       rob.arriveTime = dis_time
                   else:
                       taskID = self.encode[actionID][encodeInd]
                       preTaskID = self.encode[actionID][encodeInd - 1]
                       roadDur = self.calRoadDur(preTaskID,taskID,actionID)
                       rob.arriveTime  = rob.leaveTime + roadDur
#                   print(self.encode[actionID])
# =============================================================================
# the  task has not been cmplt
# =============================================================================
                else:
                    task = self.taskLst[taskID]
#                    self.deg.write('taskID '+ str(taskID) +'\n')
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
#                            self.deg.write(str(coordID) + '\n')
                            coordRob.leaveTime = leaveTime
                            coordRob.executeDur = coordRob.leaveTime - coordRob.arriveTime
                    rob.leaveTime = leaveTime                    
                    rob.stateType = RobotState['onTask']
                    self.decodeTime = rob.arriveTime
#                    self.deg.write('arriveChanged\n')
#                    self.saveRobotInfo()
#                    print(self.decodeTime)
# =============================================================================
#  no coordinated robot
# ============================================= ================================
#                    if not coordLst:
# =============================================================================
#  begin the leave condition for 
# =============================================================================
            if cal_type == CalType['leaveCond']:
                rob = self.robotLst[actionID]
                taskID = rob.taskID 
#                print(taskID)
                task = self.taskLst[taskID]
                if self.cmpltLst[taskID] == True:
                    print(self.cmpltLst)                    
#                    validStateBool = True
                    while True:
                        print('bug')
                        return 
                else:
                    validStateBool = task.calCurrentState(rob.leaveTime)
                    if not validStateBool :
                        break
                    if(task.isCmplt()):
                        self.cmpltLst[taskID] = True
                        self.updateEncode(taskID)                        
                        coordLst  = self.findCoordRobot(actionID)
                        for coordID in coordLst:
                            self.updateRobLeaveCond(coordID)
                    self.updateRobLeaveCond(actionID)
#                self.deg.write('taskID '+ str(taskID) +' has been cmplt\n')
#                self.deg.write('leaveChanged\n')
#                self.saveRobotInfo()
                self.decodeTime =  rob.leaveTime
            
            if cal_type == CalType['endCond']:
                invalidFitness = True
                break
            if cal_type  == CalType['backCond']:
                backBool = True
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
        if minTime < self.decodeTime:
            cal_type = CalType['backCond']
#            print(minTime)
#            print(self.decodeTime)
#        self.saveRobotInfo()
        return cal_type,actionID
    def findCoordRobot(self,robID):
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
        dis = self.taskDisMat[taskID1][taskID2]
        rob = self.robotLst[robID]
        roadDur = dis/rob.vel
        return roadDur
    def updateEncode(self,cmpltTaskID):
        self.deg2.write('cmpltTaskID = '+ str(cmpltTaskID) +'\n')
        for i in range(self.robNum):
            rob = self.robotLst[i]
#            endInd = rob.encodeIndex
            for j in range(rob.encodeIndex + 1, self.taskNum):
                if  self.encode[i][j] == cmpltTaskID:
                    self.encode[i][j] = -1
        self.saveEncode()
                    
    def updateRobLeaveCond(self,robID):
        rob = self.robotLst[robID]
        while True:
            if rob.encodeIndex  == (self.taskNum  - 1)
        rob.encodeIndex += 1
        preTaskID = rob.taskID
        if rob.encodeIndex == self.taskNum:
            rob.stopBool = True
        else:
            taskID = self.encode[robID][rob.encodeIndex]
            roadDur = self.calRoadDur(preTaskID,taskID,robID)
            rob.roadDur = roadDur
            rob.taskID = taskID
            rob.arriveTime = rob.leaveTime + rob.roadDur
            rob.stateType = RobotState['onRoad']
    def calMakespan(self):
# makespan for the MPDA problem        
        leaveTimeLst = [rob.leaveTime for rob in self.robotLst]
        makespan = max(leaveTimeLst)
        return makespan            
    def saveEncode(self):
        for i in range(self.robNum):
            lst = list(self.encode[i][:])
            rd.writeConf(self.deg2,str(i),lst)
        self.deg2.flush()
    def saveRobotInfo(self):
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
    def endDeg(self):
        self.deg.close()
        self.deg2.close()

        
if __name__ =='__main__':
    
    decode = Decode(BaseDir +'//data//s100_30_30_max100_2.5_0.02_0.02_1.2_thre0.1_MPDAins.dat')    
    for i in range(1):
        random.seed(i)
        print('seed = ',i)        
        decode.generateRandEncode()
        start = time.clock()
        makespan = decode.decode()
        print(makespan)
        end = time.clock()
        print(end - start)
    decode.endDeg()
#        
        