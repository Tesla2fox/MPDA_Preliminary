# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 14:43:38 2018

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
import copy
import collections
import time 

INF_NUM = sys.float_info.max
INF_INT_NUM = sys.maxsize
	

class EstConstructMethod(ConstructMethodBase):
    def __init__(self,instance):
        super(EstConstructMethod,self).__init__(instance)
        degFileDir = BaseDir + '//debug//'
        ins = self._instance.insFileName.split('benchmark\\')
        degFileName = degFileDir + 'deg_Min' + ins[1]
        self.deg = open(degFileName,'w')
    def constrcut(self, weightNum = 11,reverse = False):
        '''
        return the the boolean of the optimal solution 
        '''
        weightLst = self._generateWeightLst(weightNum)
        self._opt_solution = sol.Solution(self._instance)    
        start = time.clock()
        
        end = time.clock()
        self._methodPeriod = end - start
        vaild  = False                
        if self._opt_solution.objective != INF_NUM:
            vaild = True
        else:
            self.deg.write('can not get a solution \n')
        return vaild,self._opt_solution
    def _initState(self):
        
if __name__ == '__main__':
    insName = '8_9_RANDOM_CLUSTERED_MSVFLV_SVLCV_thre0.1MPDAins.dat'
    pro = ins.Instance(BaseDir + '//benchmark\\' + insName)
    e_con = EstConstructMethod(pro)
    print(e_con.constrcut())
	