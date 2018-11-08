# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 16:02:43 2018

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
    pass
else:
    sys.path.append(BaseDir)
    
from constructMethod.constructMethodBase import ConstructMethodBase,CalPeriod
        
import constructMethod.instance as ins
import constructMethod.solution as sol
import random

class RandConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(RandConstructMethod,self).__init__(instance)
    @CalPeriod()
    def construct(self,sampleTimes = 10000):
        for i in range(sampleTimes):
            resSolution = self.generateRandSol()
            resSolution.evaluate()
            if resSolution.objective < self._solution.objective:
                self._solution = resSolution
        return self._solution
    def generateRandSol(self):
        resSolution = sol.Solution(self._instance)        
        for i in range(self._instance.robNum):
            permLst = [x for x in range(self._instance.taskNum)]
            random.shuffle(permLst)
            for j in range(self._instance.taskNum):
                resSolution[(i,j)] = permLst[j]
        return resSolution
    def __str__(self):
        return 'RandConstructMethod\n' + str(self._solution)
            
    
if __name__ == '__main__':
    
    insName = '20_20_CLUSTERED_RANDOMCLUSTERED_SVLCV_LVSCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)    
    con = RandConstructMethod(pro)
#    print(pro)
#    random.seed(2)
    print(con.construct())
