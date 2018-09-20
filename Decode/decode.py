# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 14:59:38 2018

@author: robot
"""

#import 
import Decode.decodeBase as db
from Decode.decodeBase import CalType,BaseDir
import time
import sys
import copy as cp
import random
from Decode.robot import RobotState

'''
decode with re-calculation
'''
#`
class DecodeRC(db.DecodeBase):
    def __init__(self,insFileName):
        super(DecodeRC,self).__init__(insFileName)
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg_RC' + ins[1]
        self.deg = open(degFileName,'w')         
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg2_RC' + ins[1]
        self.deg2 = open(degFileName,'w')
    def decode(self):
#        circleTime = 0
        while True:
#            print('whileCircle = ',circleTime)
#            circleTime += 1
#            start = time.clock()
            self.initStates()
            cal_type = self.decodeProcessor()
#            end = time.clock()
#            print(end - start)
            if cal_type == CalType['backCond']:
                continue
            else:
                break
#        print(self.cmpltLst)
#        self.saveEncode()            
        if cal_type == CalType.stateInvalidCond:
#            print('invalidState')
#            invalidState = True
            makespan = sys.float_info.max
        else:
#            print('validState')
            makespan = self.calMakespan()
        self.saveEncode()
        return makespan
    def arriveCmpltTask(self,actionID,encodeInd):
        self.encode[actionID][encodeInd] = -1 
        rob = self.robotLst[actionID]
        while True:                       
            if len(rob.cmpltTaskLst) == 0:
                taskID = self.encode[actionID][encodeInd]
                if taskID < 0:
                    encodeInd  += 1
                    continue
                dis  = self.rob2taskDisMat[actionID][taskID]            
                dis_time = dis/rob.vel
                rob.arriveTime = dis_time
                rob.encodeIndex = encodeInd
                break
            else:
                if encodeInd == self.taskNum - 1:
                    rob.stopBool = True
                    break
                taskID = self.encode[actionID][encodeInd]                   
                if taskID < 0:
                    encodeInd  += 1
                    continue
                preTaskID = rob.cmpltTaskLst[-1]
                roadDur = self.calRoadDur(preTaskID,taskID,actionID)
                rob.arriveTime  = rob.leaveTime + roadDur
                rob.encodeIndex = encodeInd
                break           
        rob.taskID = taskID 
    
'''
decode with save state
'''
class DecodeSS(db.DecodeBase):
    def __init__(self,insFileName):
        super(DecodeSS,self).__init__(insFileName)
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg_SS' + ins[1]
        self.deg = open(degFileName,'w')         
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg2_SS' + ins[1]
        self.deg2 = open(degFileName,'w')
    def decode(self):
#        circleTime = 0
#        self.saveEncode()
        self.initStates()
        self.robInfoLst = []
        self.taskInfoLst = []
        self.decodeTimeLst = []            
        while True:
#            print('whileCircle = ',circleTime)
#            circleTime += 1
#            if circleTime > 100:
#                break
#            start = time.clock()
#            print(self.cmpltLst)
            cal_type = self.decodeProcessor()
#            self.saveEncode()
#            end = time.clock()
#            print(end - start)
            if cal_type == CalType['backCond']:
#                break                
                while True:
                    if self.decodeTimeLst[-1] > self.backArriveTime:
                        self.decodeTimeLst.pop()
                        self.robInfoLst.pop()
                        self.taskInfoLst.pop()
                    else:
                        break
#                print('lastDecode',self.decodeTimeLst[-1])
#                print('backArriveTime',self.backArriveTime)
#                print('backRobId',self.backRobID)
#                print('')
                self.eventRecover()
#                self.deg.write('__backItem__\n')
#                self.saveRobotInfo()
#                break    
                continue
            else:
                break
#        print('end = ',self.cmpltLst)
        if cal_type == CalType.stateInvalidCond:
            makespan = sys.float_info.max
        else:
            makespan = self.calMakespan()
        self.saveEncode()
        return makespan
    def saveEventInMemory(self):        
        robInfo = []
        for rob in self.robotLst:
            variableInfo = rob.variableInfo()
            robInfo.append(cp.deepcopy(variableInfo))
#            robInfoTuple += variableInfo
        self.robInfoLst.append(cp.deepcopy(robInfo))
        taskInfo = []
        for task in self.taskLst:
            variableInfo = task.variableInfo()
            taskInfo.append(variableInfo)    
        self.taskInfoLst.append(taskInfo)
        self.decodeTimeLst.append(self.decodeTime)
    def backOneStep(self):
        self.robInfoLst.pop()
        self.taskInfoLst.pop()
        self.decodeTimeLst.pop()
        self.decodeTime = self.decodeTimeLst[-1]        
    def eventRecover(self):
        robInfo = self.robInfoLst[-1]
        self.decodeTime = self.decodeTimeLst[-1]
#        print(robInfoTuple)
        for index,rob in enumerate(self.robotLst):            
            rob.recover(*robInfo[index])
        backRob = self.robotLst[self.backRobID]
#        backInfo = self.backInfo
        backRob.recover(*self.backInfo)
        taskInfo = self.taskInfoLst[-1]
        for index,task in enumerate(self.taskLst):            
            task.recover(*taskInfo[index])
            self.cmpltLst[index]  = task.cmplt
    def arriveCmpltTask(self,actionID,encodeInd):
        self.encode[actionID][encodeInd] = -1 
        rob = self.robotLst[actionID]
        while True:                       
            if len(rob.cmpltTaskLst) == 0:
                taskID = self.encode[actionID][encodeInd]
                if taskID < 0:
                    encodeInd  += 1
                    continue
                dis  = self.rob2taskDisMat[actionID][taskID]            
                dis_time = dis/rob.vel
                rob.arriveTime = dis_time
                rob.encodeIndex = encodeInd
                break
            else:
                if encodeInd == self.taskNum - 1:
                    rob.stopBool = True
                    break
                taskID = self.encode[actionID][encodeInd]                   
                if taskID < 0:
                    encodeInd  += 1
                    continue
                preTaskID = rob.cmpltTaskLst[-1]
                roadDur = self.calRoadDur(preTaskID,taskID,actionID)
                rob.arriveTime  = rob.leaveTime + roadDur
                rob.encodeIndex = encodeInd
                break           
        rob.taskID = taskID
        self.backOneStep()
'''
decode no-backtrack
'''

class DecodeNB(db.DecodeBase):
    def __init__(self,insFileName):
        super(DecodeNB,self).__init__(insFileName)
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg_NB' + ins[1]
        self.deg = open(degFileName,'w')         
        degFileDir = BaseDir + '//debug//'
        ins = self.insFileName.split('data\\')
        degFileName = degFileDir + 'deg2_NB' + ins[1]
        self.deg2 = open(degFileName,'w')
        self.leaveCmpltTask = self.updateRobLeaveCond
    def decode(self):
        self.initStates()
        cal_type = self.decodeProcessor()
        if cal_type == CalType.stateInvalidCond:
#            print('invalidState')
#            invalidState = True
            makespan = sys.float_info.max
        else:
#            print('validState')
            makespan = self.calMakespan()
        self.saveEncode()
        return makespan
    def arriveCmpltTask(self,actionID,encodeInd):
        rob = self.robotLst[actionID]
        rob.leaveTime = rob.arriveTime
        rob.stateType = RobotState['onTask']
        self.decodeTime = rob.arriveTime
#    def leaveCmpltTask(self,actionID):

if __name__ == '__main__':
    insName = 's100_80_80_max100_2.5_0.02_0.02_1.2_thre0.1_MPDAins.dat'
    d_rc = DecodeRC(BaseDir + '//data//' + insName)    
    d_ss = DecodeSS(BaseDir + '//data//' + insName)
    d_nb = DecodeNB(BaseDir + '//data//' + insName)    
    random.seed(1)
    d_nb.generateRandEncode()
    d_nb.saveEncode()
    makespan = d_nb.decode()
    print('nb_makespan = ',makespan)
    random.seed(1)
    d_rc.generateRandEncode()
    d_rc.saveEncode()
    makespan = d_rc.decode()
    print('rc_makespan = ',makespan)
    random.seed(1)    
    d_ss.generateRandEncode()
    d_ss.saveEncode()
    makespan = d_ss.decode()
    print('ss_makespan = ',makespan)
    encode = d_ss.genNoBacktrackEncode()
    d_nb.encode = encode
    makespan = d_nb.decode()
    print('newNb_makespan = ',makespan)    
    d_rc.endDeg()
    d_ss.endDeg()
    d_nb.endDeg()

    
    