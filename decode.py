# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 10:12:55 2018

@author: robot
"""

from read_cfg import *
import numpy as np
class Decode:
    def __init__(self,insFileName):
        readCfg = Read_Cfg(insFileName)
#        ins_pic  = Pic()
        self.robNum = int(readCfg.getSingleVal('robNum')) 
        self.tskNum = int(readCfg.getSingleVal('tskNum'))
        self.robAbiLst  = []
        self.robVelLst = []
        self.tskStateLst = []
        self.tskRatLst = []
        readCfg.get('rob_abi',self.robAbiLst)
        readCfg.get('rob_vel',self.robVelLst)
        readCfg.get('tsk_rat',self.tskRatLst)
        readCfg.get('tsk_state',self.tskStateLst)
        rob2tskDisMat = np.zeros((self.robNum,self.tskNum))
        disLst = []
        readCfg.get('rob2tskDis',disLst)
        for i in range(self.robNum):
            for j in range(self.tskNum):
                rob2tskDisMat[i][j] = disLst[i*self.robNum+j]
                
        tskDisMat = np.zeros((self.tskNum,self.tskNum))
        disLst = []
        readCfg.get('tskDis',disLst)
        for i in range(self.tskNum):
            for j in range(self.tskNum):
                tskDisMat[i][j] = disLst[i*self.tskNum+j]

                
        print(tskDisMat)
        print(self.tskStateLst)
        
#        rob_x = []
#        readCfg.get('rob_x',rob_x)
#        rob_y = []
#        readCfg.get('rob_y',rob_y)
#        print('begin')    
#        ins_pic.addRob(rob_x,rob_y)
#    
#        tsk_x = []
#        readCfg.get('tsk_x',tsk_x)
#        tsk_y = []
#        readCfg.get('tsk_y',tsk_y)
#        ins_pic.addTsk(tsk_x,tsk_y)
        
        
if __name__ =='__main__':
    decode = Decode('./data//s100_8_10_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.txt')
    
            
        