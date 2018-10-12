# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 16:21:32 2018

the benchmark constructed by the paper {
New Benchmark Instances for the Capacitated Vehicle Routing Problem
}
@author: robot
"""

from enum import Enum
import random
import math
import numpy as np
import readCfg.read_cfg as rd
from scipy.spatial.distance import pdist
import datetime 

#import enum


'''
CNETRAL means all robots are in point(50,50)
ECCENTRIC means all robots are in the corner (0,0) of the work space
RANDOM
CLUSTED 
SV = small value
LCV = large CV
'''
class POSDIS(Enum):
    CENTRAL = 0  
    ECCENTRIC = 1
    RANDOM = 2
    CLUSTERED = 3
    RANDOMCLUSTERED = 4
#    Eccentric 
    
class VALUEDIS(Enum):
    UNITARY = 0
    SVLCV = 1
    SVSCV = 2
    LVLCV = 3
    LVSCV = 4
    QUADRANT = 5
# many small values, few large values
    MSVFLV = 6


def EuclideanDis(tup1 = (0,0), tup2 = (0,0)):
    vec1 = np.array(tup1)
    vec2 = np.array(tup2)
    X_sci = np.vstack([vec1,vec2])
    dis = float(pdist(X_sci))
    return dis

class Point(object):
    def __init__(self,x = 0,y = 0):
        self.x = x
        self.y = y
    def __eq__(self,other):
        if self.x==other.x and self.y==other.y:
            return True
        return False
    def __str__(self):
        return "x:"+str(self.x)+",y:"+str(self.y)
    def distance(self, x = 0, y= 0):
        x2 = (self.x - x)**2
        y2 = (self.y - y)**2
        return math.sqrt(x2 + y2)



#for insInd in range(insNum):
    
def generatePos(posNum,posType):
    def clusteredPos(posNum):
        resLst = []
        seedNum = random.randint(3,8)
        if seedNum > posNum :
            seedNum  = posNum
        seedPosLst = [Point(random.randint(0,100),random.randint(0,100)) \
                  for x in range(seedNum)]        
        resLst.extend(seedPosLst)
        probMidLst = []
        sumProb = 0
        for x in range(101):
            for y in range(101):
                probability = 0
                for seedPos in seedPosLst:
                    dis = seedPos.distance(x = x, y = y)
                    probability  += math.exp(-dis/4)
                sumProb += probability
                probMidLst.append((x,y,probability))    
        probLst = []
        prob = 0
        for probUnit in probMidLst:
            probIncre = probUnit[2]/sumProb
            prob += probIncre
            probLst.append((probUnit[0],probUnit[1],prob))
        for u in range(posNum - seedNum):
            prob = random.random()
            for probUnit in probLst:
                if prob< probUnit[2]:
                    resLst.append(Point(probUnit[0],probUnit[1]))
                    break
        return resLst
    if posType == POSDIS['CENTRAL']:
        resLst = [Point(50,50) for x in range(posNum)]
    if posType == POSDIS['ECCENTRIC']:
        resLst = [Point(0,0) for x in range(posNum)]
    if posType == POSDIS['RANDOM']:
        resLst = [Point(random.randint(0,100),random.randint(0,100)) \
                  for x in range(posNum)]
    if posType == POSDIS['CLUSTERED']:                            
        resLst = clusteredPos(posNum)
    if posType == POSDIS['RANDOMCLUSTERED']:
        randomNum = math.ceil(posNum/2)
        clusteredNum = posNum - randomNum
        resLst = [Point(random.randint(0,100),random.randint(0,100)) \
                  for x in range(randomNum)]
        resLst.extend(clusteredPos(clusteredNum))
#        print(seedPosLst)
    return resLst


def generateRate(rateNum,rateType,posLst = []):
    if rateType == VALUEDIS['UNITARY']:
        resLst = [0.2 for x in range(rateNum)]
    if rateType == VALUEDIS['SVLCV']:
        resLst = [random.uniform(0.02,0.2) for x in range(rateNum)]
    if rateType == VALUEDIS['SVSCV']:
        resLst = [random.uniform(0.02,0.1) for x in range(rateNum)]
    if rateType == VALUEDIS['LVLCV']:
        resLst = [random.uniform(0.02,2) for x in range(rateNum)]
    if rateType == VALUEDIS['LVSCV']:
        resLst = [random.uniform(0.2,2) for x in range(rateNum)]
    if rateType == VALUEDIS['QUADRANT']:
        resLst = []    
        for pos in posLst:
            x_bias = pos.x - 50
            y_bias = pos.y - 50
            if x_bias*y_bias > 0:
                resLst.append(random.uniform(0.02,1))
            else:
                resLst.append(random.uniform(1,2))
    if rateType == VALUEDIS['MSVFLV']:
        svNum = math.ceil(random.uniform(0.7,0.95)*rateNum)
        resLst = [random.uniform(0.02,0.2) for x in range(svNum)]
        lvNum = rateNum - svNum
        lvLst = [random.uniform(0.2,2) for x in range(lvNum)]
        resLst.extend(lvLst)                
    return resLst

def writeConf(robNum,taskNum,combConf):
    robPosLst = generatePos(robNum,combConf[0])
    robAbiLst = generateRate(robNum,combConf[2],robPosLst)
    robPosLst  = [(robPos.x,robPos.y) for robPos in robPosLst]  
    robVelLst = [1 for x in range(robNum)]
    sum_robAbi  = sum(robAbiLst)
    taskPosLst = generatePos(taskNum,combConf[1])
    taskRateLst = generateRate(taskNum,combConf[3],taskPosLst)
# deal with the unable instance
    for i in range(len(taskRateLst)):
        taskRate = taskRateLst[i]
        while taskRate*robNum/2 > sum_robAbi:
            taskRate *= random.uniform(0.5,1)
        taskRateLst[i] = taskRate
    taskPosLst  = [(taskPos.x,taskPos.y) for taskPos in taskPosLst]  
    taskStateLst = [1 for i in range(taskNum)]    
    comp_threhold = 0.1
    
    rob2tskDisMat = np.zeros((robNum,taskNum))
    rob2tskDisLst = []
    for i in range(robNum):
        for j in range(taskNum):
            d2 = float(EuclideanDis(robPosLst[i],taskPosLst[j]))
            rob2tskDisMat[i][j] = d2
            rob2tskDisLst.append(d2)
            
    tskDisLst = []
    tskDisMat = np.zeros((taskNum,taskNum))
    for i in range(taskNum):
        for j in range(taskNum):
            d2 = EuclideanDis(taskPosLst[i],taskPosLst[j])
            tskDisMat[i][j] = d2
            tskDisLst.append(d2)
    nameLst = []
    nameLst.append(robNum)
    nameLst.append(taskNum)
    for disType in combConf:
        nameLst.append(disType.name)
    nameLst.append('thre'+str(comp_threhold))
    nameLst = [str(x) for x in nameLst]
    sep = '_'
    sep =sep.join(nameLst)
    insFileDir = '.\\benchmark\\'
    insFileName = insFileDir + sep +'MPDAins.dat'
    f_ins  = open(insFileName,'w')
    f_ins.write('time '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\n')
    f_ins.write(sep+'\n')
    rd.writeConf(f_ins,'robNum',[robNum])
    rd.writeConf(f_ins,'taskNum',[taskNum])
#    writeConf(f_ins,'max_cordx',[max_cordx])
#    writeConf(f_ins,'max_cordy',[max_cordy])
#    writeConf(f_ins,'max_vel',[max_vel])
#    writeConf(f_ins,'max_abi',[max_abi])
#    writeConf(f_ins,'max_rat',[max_rat])
#    writeConf(f_ins,'max_state',[max_state])
    rd.writeConf(f_ins,'comp_threhold',[comp_threhold])
    rd.writeConf(f_ins,'rob2tskDis',rob2tskDisLst)
    rd.writeConf(f_ins,'tskDis',tskDisLst)

    f_ins.write('\n')    
    rob_xLst = [x[0] for x in robPosLst]
    rob_yLst = [y[1] for y in robPosLst]
    rd.writeConf(f_ins,'rob_x',rob_xLst)
    rd.writeConf(f_ins,'rob_y',rob_yLst)
    rd.writeConf(f_ins,'rob_vel',robVelLst)
    rd.writeConf(f_ins,'rob_abi',robAbiLst)

    f_ins.write('\n')    
    tsk_xLst = [x[0] for x in taskPosLst]
    tsk_yLst = [y[1] for y in taskPosLst]
    rd.writeConf(f_ins,'tsk_x',tsk_xLst)    
    rd.writeConf(f_ins,'tsk_y',tsk_yLst)
    rd.writeConf(f_ins,'tsk_rat',taskRateLst)
    rd.writeConf(f_ins,'tsk_state',taskStateLst)
    f_ins.close()
#nameLst.append(combConf[0])
#    1
#    for 
#    print(probLst)
#    print(sumProb)
    
    
insNum = 20
    
if __name__ == '__main__':
    
    min_robNum = 2
    min_taskNum = 2
    max_robNum = 100
    max_taskNum = 100
    insNum = 20
    
    numConfLst = []
    all_combConfLst = []
    numLst = list(range(min_robNum,50,3))
    posTypeLst = list(POSDIS)
    valueTypeLst = list(VALUEDIS)

    print(numLst)
    seedInd = 0
    for i in range(len(numLst)):
        robNum = numLst[i]
        taskNum = numLst[i]
        numConfLst.append((robNum,taskNum))        
        random.seed(seedInd)
        seedInd += 1
        combConfLst = []
        for i in range(4):
            while True:
                 robPosType = posTypeLst[random.randint(0,4)]
                 taskPosType = posTypeLst[random.randint(0,4)]
                 robRateType = valueTypeLst[random.randint(0,6)]
                 taskRateType = valueTypeLst[random.randint(0,6)]             
                 confTuple = (robPosType,taskPosType,robRateType,taskRateType)
                 if confTuple not in combConfLst:
                     combConfLst.append(confTuple)
                     break
        all_combConfLst.append(combConfLst)     
        random.seed(seedInd)
        seedInd += 1
        while True:            
            c_taskNum = random.randint(math.ceil(taskNum*0.5),math.ceil(taskNum*1.5))
            if c_taskNum != taskNum:
                break
        numConfLst.append((robNum,c_taskNum))
        combConfLst = []
        for i in range(4):
            while True:
                 robPosType = posTypeLst[random.randint(0,4)]
                 taskPosType = posTypeLst[random.randint(0,4)]
                 robRateType = valueTypeLst[random.randint(0,6)]
                 taskRateType = valueTypeLst[random.randint(0,6)]             
                 confTuple = (robPosType,taskPosType,robRateType,taskRateType)
                 if confTuple not in combConfLst:
                     combConfLst.append(confTuple)
                     break
        all_combConfLst.append(combConfLst)     

        
#    print(combConfLst)

    
#    if POSDIS['CENTRAL'] == posTypeLst[0]:
#        print(str(posTypeLst[0]))
#        taskNum = numLst[i]
    print(len(numConfLst))
    print(len(all_combConfLst))
    for i in range(len(numConfLst)):        
        robNum = numConfLst[i][0]
        taskNum = numConfLst[i][1]
        for combConf in all_combConfLst[i]:
            writeConf(robNum,taskNum,combConf)
#            break
#        break
#            robPos = generatePos(robNum,combConf[0])
#            taskPos = generatePos(taskNum,combConf[1])
#            rob_abi = generateRate(robNum,combConf[2],robPos)
#            task_rate = generateRate(taskNum,combConf[3],taskPos)
        
#    print(numConfLs)
#    for num in numLst:
#        robNum = num
#        taskNum = 
    
#    for numLst in 
#    for i in range(15):
#        robNum = 
#    for 
    confLst = []
    random.seed(1)
    print(random.seed())
    print(list(POSDIS)[4])    
#    print(POSDIS.CLUSTERED.)
#    lst = generatePos(2,POSDIS['RANDOMCLUSTERED'])
#    for p in lst:
#        print(p)
#    print(lst)
    print(random.randint(0,1))
    A = Point(3,3)
    B = Point(3,4)
    if A == B :
        print('wtf')
    print(A)
    print(POSDIS.RANDOMCLUSTERED)
#    print(VALUEDIS.__str__)
    wtf = list(enumerate(VALUEDIS))
    print(wtf)