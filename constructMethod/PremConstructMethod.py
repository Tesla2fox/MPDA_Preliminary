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
#    print('have been added')
    pass
else:
    sys.path.append(BaseDir)
    
from constructMethod.constructMethodBase import ConstructMethodBase,CalPeriod
        
import constructMethod.instance as ins
import constructMethod.solution as sol
import random
import itertools


class PermutationException(Exception):
    '''
    Custom exception types about PermutationException
    '''
    def __init__(self):
        err = 'PermutationException'
        super(PermutationException,self).__init__(err)
        
class PremConstructMethod(ConstructMethodBase):
    def __init__(self, instance):
        super(PremConstructMethod,self).__init__(instance)
    @CalPeriod()
    def construct(self,sampleTimes = 10000):
        if self._instance.robNum <= 4 and self._instance.taskNum <=5:
            permLst = [x for x in range(self._instance.taskNum)]
            permLst = list(itertools.permutations(permLst,self._instance.taskNum))
            encodeLst = itertools.product(permLst,repeat = self._instance.robNum)
            for encode in encodeLst:
                resSolution = sol.Solution(self._instance)
                for i in range(self._instance.robNum):
                    for j in range(self._instance.taskNum):
                        resSolution[(i,j)] = encode[i][j]
                resSolution.evaluate()
                if resSolution.objective <self._solution.objective:
                    self._solution = resSolution
                pass
        else:
            raise PermutationException()        
        return self._solution    
    def __str__(self):
        return 'PremConstructMethod\n' + str(self._solution)
            
    
if __name__ == '__main__':
    
    insName = 's100_3_4_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.dat'
    pro = ins.Instance(BaseDir + '//data\\' + insName)    
    con = PremConstructMethod(pro)
#    con.construct()
    
#    print(pro)
#    random.seed(2)
    print(con.construct())
#    constructName = 's100_5_10_max100_2.5_2.5_2.5_1.2_thre0.1_MPDAins.dat'    
#    con = ConstructMethodBase(BaseDir + '//data\\' + constructName)
#    print(con)
#    print('wtf')
        