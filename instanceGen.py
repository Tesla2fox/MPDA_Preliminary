# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 20:59:57 2018

@author: robot


this is an instance generator
"""

import time 
import datetime 
import random
import math
from random import randint
import copy
import read_cfg as rd
from read_cfg import *
import numpy as np
from scipy.spatial.distance import pdist


    
def EuclideanDis(tup1 = (0,0), tup2 = (0,0)):
    vec1 = np.array(tup1)
    vec2 = np.array(tup2)
    X_sci = np.vstack([vec1,vec2])
    dis = float(pdist(X_sci))
    return dis




if __name__ == '__main__':
    randomSeed = 100
    random.seed(randomSeed)
    
    robNum = 20
    tskNum = 50
    max_cordx = 100
    max_cordy = 100
    max_vel = 2.5
    max_abi = 0.02
    max_rat = 0.02
    max_state = 1.2
    comp_threhold = 0.1
    
# =============================================================================
#   the max threhold should not be considered, because the MPDA problem has been
#   complex enough
# =============================================================================
    max_constraint = 1000
#    range_x = [0 , 100]
    
    robPosLst = []
    robVelLst = []
    robAbiLst = []    
    while len(robPosLst)<robNum:
        rob_x = random.randint(0,max_cordx)
        rob_y = random.randint(0,max_cordy)
        rob_vel = random.random() * max_vel
        robVelLst.append(rob_vel)
        rob_abi = random.random() * max_abi
        robAbiLst.append(rob_abi)
        robPosLst.append((rob_x,rob_y))
   
    tskPosLst = []
    tskStateLst = []
    tskRatLst = []
    while len(tskPosLst) <tskNum:
        tsk_x = random.randint(0,max_cordx)
        tsk_y = random.randint(0,max_cordy)
        tskPosLst.append((tsk_x,tsk_y))
        while True:            
            tsk_s = random.random() * max_state
            if tsk_s > comp_threhold:
                break
        tskStateLst.append(tsk_s)
        tsk_rat = random.random() * max_rat
        tskRatLst.append(tsk_rat)        
    rob2tskDisMat = np.zeros((robNum,tskNum))
   
    rob2tskDisLst = []
#    print(len(rob2tskDisMat))
    for i in range(robNum):
        for j in range(tskNum):
            d2 = float(EuclideanDis(robPosLst[i],tskPosLst[j]))
            rob2tskDisMat[i][j] = d2
            rob2tskDisLst.append(d2)
            
    tskDisLst = []
    tskDisMat = np.zeros((tskNum,tskNum))
    for i in range(tskNum):
        for j in range(tskNum):
            d2 = EuclideanDis(tskPosLst[i],tskPosLst[j])
            tskDisMat[i][j] = d2
            tskDisLst.append(d2)

    nameLst =[]
    nameLst.append('s'+str(randomSeed))
    nameLst.append(robNum)
    nameLst.append(tskNum)
    nameLst.append('max'+str(max_cordx))
    nameLst.append(max_vel)
    nameLst.append(max_abi)
    nameLst.append(max_rat)
    nameLst.append(max_state)
    nameLst.append('thre'+str(comp_threhold))
    nameLst = [str(x) for x in nameLst]
    sep = '_'
    sep = sep.join(nameLst)
    insFileDir = './data//'
    insFileName = insFileDir + sep +'_MPDAins.dat'
    
    print(repr(insFileName))
    f_ins  = open(insFileName,'w')
    f_ins.write('time '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\n')

    writeConf(f_ins,'robNum',[robNum])
    writeConf(f_ins,'tskNum',[tskNum])
    writeConf(f_ins,'max_cordx',[max_cordx])
    writeConf(f_ins,'max_cordy',[max_cordy])
    writeConf(f_ins,'max_vel',[max_vel])
    writeConf(f_ins,'max_abi',[max_abi])
    writeConf(f_ins,'max_rat',[max_rat])
    writeConf(f_ins,'max_state',[max_state])
    writeConf(f_ins,'comp_threhold',[comp_threhold])
    writeConf(f_ins,'rob2tskDis',rob2tskDisLst)
    writeConf(f_ins,'tskDis',tskDisLst)

    f_ins.write('\n')    
    rob_xLst = [x[0] for x in robPosLst]
    rob_yLst = [y[1] for y in robPosLst]
    writeConf(f_ins,'rob_x',rob_xLst)
    writeConf(f_ins,'rob_y',rob_yLst)
    writeConf(f_ins,'rob_vel',robVelLst)
    writeConf(f_ins,'rob_abi',robAbiLst)

    f_ins.write('\n')    
    tsk_xLst = [x[0] for x in tskPosLst]
    tsk_yLst = [y[1] for y in tskPosLst]
    writeConf(f_ins,'tsk_x',tsk_xLst)    
    writeConf(f_ins,'tsk_y',tsk_yLst)
    writeConf(f_ins,'tsk_rat',tskRatLst)
    writeConf(f_ins,'tsk_state',tskStateLst)
    rob2tskDisMat
    print(sep)
    print(nameLst)    
    
    
    f_ins.close()
#    print(tskDisMat)
##    p =  1
##    print(vars())
#    print(rob2tskDisMat)
#    print(robPosLst)
#    maxVel = 10
#    minVel = 10    
    

