# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:24:02 2018

the EDA metho for the MPDA problem
@author: robot
"""
import pprint
import decode as dc
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


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
        self.popFitness = []
# statisticMat list 
        self.sMatLst = []
    def process(self):
        self.generatePop()
        self.calPopFitness()
        print(self.popFitness)
        s_lst = self.selection()
        self.statistic(s_lst)
        self.model()
        for i in range(self.maxIter):
            pass
            
        
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
        
#        print(sMatLst)
    def model(self):
        X = []
        for i in range(self.taskNum):
             X.append([i, self.sMatLst[0][0][i]])
        kmeans = KMeans(n_clusters = 2)
        kmeans.fit(X)
        print(X)
        y_kmeans = kmeans.predict(X)
        centers = kmeans.cluster_centers_
        plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
        plt.scatter([x[0] for x in X], [x[1] for x in X], c=y_kmeans, cmap='viridis')


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
        
        


if __name__ == '__main__':
    print('__')
    eda_method = EDA('./data//s100_10_10_max100_2.5_0.02_0.02_1.2_thre0.1_MPDAins.dat',
                     100,
                     0.3)
    eda_method.display()
    eda_method.process()
#    u = 10
    

        
        