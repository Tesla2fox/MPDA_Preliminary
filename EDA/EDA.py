# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:24:02 2018

the EDA metho for the MPDA problem
@author: robot
"""


import os,sys
print(__file__)
AbsolutePath = os.path.abspath(__file__)           
#将相对路径转换成绝对路径
SuperiorCatalogue = os.path.dirname(AbsolutePath)   
#相对路径的上级路径
print(AbsolutePath)
print(SuperiorCatalogue)
BaseDir = os.path.dirname(SuperiorCatalogue)
print(BaseDir)        
#在“SuperiorCatalogue”的基础上在脱掉一层路径，得到我们想要的路径。
if BaseDir in sys.path:
    pass
else:
    sys.path.append(BaseDir)



import pprint
import Decode.decode as dc
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
import copy as cp



random.seed(105)


      

class EDA:
    def __init__(self,insName = './data//s100_80_80_max100_2.5_0.02_0.02_1.2_thre0.1_MPDAins.dat',
                 NP = 100,
                 ratio = 0.3
                 ,maxIter = 600):
        self.insName = insName 
        self.NP = NP
        self.ratio = ratio
        self.modelSize = math.ceil(NP*ratio)
        self.decode = dc.Decode(insName)
        self.robNum = self.decode.robNum
        self.taskNum = self.decode.taskNum
        self.maxIter = maxIter
        self.pop = []
#         child pop
        self.c_pop = []
        self.popFitness = []
# statisticMat list 
        self.sMatLst = []
    def process(self):
        self.generatePop()
#        print(len(self.pop))
        min_fLst = []
        for i in range(self.maxIter):
            self.calPopFitness()
            print('gen = ', i)
#            print(self.popFitness)
            s_lst = self.selection()
            min_fLst.append(self.popFitness[s_lst[0]])
            self.c_pop = []
            for ind in s_lst:
                self.c_pop.append(self.pop[ind])
            self.statistic(s_lst)
            self.model()
            self.sample()
            self.pop = self.c_pop
            pass
        print(min_fLst)
        
    def generatePop(self):
        for i in range(self.NP):
            self.pop.append(self.generateRandEncode())            
        print(len(self.pop))
    def calPopFitness(self):
        self.popFitness = []
        for encode in self.pop:
            makespan = self.calFitness(encode)
            self.popFitness.append(makespan)
    def selection(self):
        enumSeq = enumerate(self.popFitness)
        enumSeq = sorted(enumSeq,key = lambda x: x[1])
        selectPop = []
        for index,makespan in enumSeq:
            selectPop.append(index)
            if len(selectPop) >= self.modelSize:            
                break
        return selectPop    
    def statistic(self, s_lst = []):
        self.sMatLst = []
        for i in range(self.robNum):
            mat = np.zeros((self.taskNum,self.taskNum),dtype = int)
            self.sMatLst.append(mat)
#        print(sMatLst)        
        for i in range(self.robNum):
            sMat = self.sMatLst[i]
            for index  in s_lst:
                robEncode = self.pop[index][i]
                for pos in range(len(robEncode)):
                    taskID = robEncode[pos]
                    sMat[pos][taskID] += 1
    def model(self):
        self.modelLst = []
        for robInd in range(self.robNum):
            robModel = []
            for taskPos in range(self.taskNum):
#                print('robId = ',robInd, 'taskPos',taskPos)
                data = []
                for i in range(self.taskNum):
                     data.append([i, self.sMatLst[robInd][taskPos][i]])
                kmeans = KMeans(n_clusters = 2)
                kmeans.fit(data)
                y_kmeans = kmeans.predict(data)
                poptLst = []
                for i in range(2):
                    x_lst = []
                    y_lst = []
                    for x,setInd in enumerate(y_kmeans):
                        if setInd == i:
                            x_lst.append(x)
                            y_lst.append(data[x][1])
                    x_lst = np.array(x_lst)
                    y_lst = np.array(y_lst)
                    mean = sum(x_lst*y_lst)/sum(y_lst)
                    sigma = np.sqrt(sum(y_lst * (x_lst - mean)**2) / sum(y_lst))
                    try:                        
                        popt,pcov = curve_fit(Gauss, x_lst, y_lst, p0=[max(y_lst), mean, sigma], maxfev= 3500)
                    except:
                        popt = [max(y_lst), mean, sigma]
                    ratio = sum(y_lst)/self.modelSize
                    poptLst.append((ratio,popt))
                robModel.append(tuple(poptLst))               
            self.modelLst.append(robModel)
    def sample(self):        
        while len(self.c_pop) < self.NP:            
            sampleMat = np.zeros((self.robNum,self.taskNum))
            for robInd in range(self.robNum):
                for taskPos in range(self.taskNum):
                    robModel = self.modelLst[robInd][taskPos]
                    popt = []
                    if random.random() < robModel[0][0]:
                        popt = robModel[0][1]
                    else:
                        popt = robModel[1][1]
                    x = random.normalvariate(popt[1],popt[2])
                    sampleMat[robInd][taskPos] = x
    #        sampleMat 2 the encode mat
            encodeMat = np.zeros((self.robNum,self.taskNum),dtype = int)
            for robInd in range(self.robNum):
                 enumPerm = list(enumerate(sampleMat[robInd][:]))
    #             print()
                 enumPerm = sorted(enumPerm,key = lambda x: x[1])
#                 print(enumPerm)
                 encodeMat[robInd][:] = [x[0] for x in enumPerm]
#            print(encodeMat)
            self.c_pop.append(encodeMat)
#                y = Gauss(x,*popt)
                       
                
    def generateRandEncode(self):
        encode = np.zeros((self.robNum,self.taskNum),dtype = int)
        for i in range(self.robNum):
#            for j in range(self.taskNum):
            permLst = [x for x in range(self.taskNum)]
            random.shuffle(permLst)
#            print(permLst)
            encode[i][:] = permLst
        return encode
    def calFitness(self,encode = np.array([])):
        self.decode.encode = encode
        makespan = self.decode.decode()
        return makespan 
    def display(self):
        pprint.pprint((self.insName,
                      self.NP,
                      self.ratio))
        
#  a = amplitude        
def Gauss(x,a,x0,sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))/(math.sqrt(2*math.pi)*sigma)
  

if __name__ == '__main__':
    print('__')
    eda_method = EDA( BaseDir + './data//s100_5_6_max100_2.5_0.02_0.02_1.2_thre0.1_MPDAins.dat',
                     100,
                     0.3,
                     300)
    eda_method.display()
    eda_method.process()
    
    

        
        