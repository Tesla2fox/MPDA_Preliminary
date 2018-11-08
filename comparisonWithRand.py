# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 09:22:29 2018

@author: robot
"""

from constructMethod import *
import os
import pickle
import dataProcess.dataProcess as dp
import collections
from enum import Enum

'''
STATS is the abbreviation for statistic
'''
STATS_index = collections.namedtuple('STATS_index',['objective','period'])

class MethodType(Enum):
    SR1 = 1
    SR2 = 2
    MR1 = 3
    MR2 = 4

methodExdic = dict()
methodExdic[0] = MethodType.SR1
methodExdic[1] = MethodType.SR2
methodExdic[2] = MethodType.MR1
methodExdic[3] = MethodType.MR2



TableTuple = collections.namedtuple('TableTuple',['SR1','SR2','MR1','MR2','Rand'])
# =============================================================================
# the first means  the objective better than the random method
# the second means the calculation period better than the random alg
# the 3rd means the best objective in all methods\
# the 4th means the best calculation period in all methods
# =============================================================================
g_statisticRes =  []
for i in range(5):
    g_statisticRes.append([0,0,0,0])


def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
        pass
#        print('dirs are ',dirs) #当前路径下所有子目录  
#        print('root is ',root) #当前目录路径  
#        print('files are',files) #当前路径下所有非目录子文件
    return root,dirs,files


def data2Latex (tableUnit,fileName):

    def getTextbf(lst = []):
        min_val = min(lst)
        min_ValInd = lst.index(min_val) 
#        print(' '.join(lst))
        strLst = [dp.Etype2str(x,sDigit = 3) for x in lst]
        strLst[min_ValInd] = '\\textbf{' +strLst[min_ValInd] + '}'
        resStr = str()
        for unit in strLst:
            resStr  += ' & ' + unit
#        strLst = ' & '.join(strLst)
        print(resStr)
        return resStr
    latexStr = str()
    fileName = fileName.split('_')
    fileName = fileName[:-1]
    
    print('fileName = ',fileName)
    latexStr = ' & '.join(fileName)    
    lst = []
    worseIndex = []
    for i in range(len(tableUnit)):
        unit = tableUnit[i]
        lst.append(unit.objective)
        if i == (len(tableUnit) - 1):
            break
        if unit.objective > tableUnit[-1].objective:
            worseIndex.append(i)
        else:
            g_statisticRes[i][0] += 1 
    min_val = min(lst)
    minIndex = []
    for i in range(len(lst)):
        if min_val == lst[i]:
            minIndex.append(i)
            g_statisticRes[i][2] += 1
            
#    min_valInd = lst.index(min_val)    
    strLst = [dp.Etype2str(x,sDigit = 3) for x in lst]
    for i in worseIndex:
        strLst[i] = '\\textcolor{gray}{' + strLst[i] + '}'        
    for i in minIndex:
        strLst[i] = '\\textbf{' +strLst[i] + '}'
    resStr = str()
    for unit in strLst:
        resStr  += ' & ' + unit
    latexStr  += resStr        
    latexStr  += '\\'
    latexStr  += '\\'
    
    latexStr  += '\n'
    
    latexStr  += '\\multicolumn{6}{c}{}	'
    lst = []
    worseIndex = []
    for i in range(len(tableUnit)):
        unit = tableUnit[i]
        lst.append(unit.period)
        if i == (len(tableUnit) - 1):
            break
        if unit.period > tableUnit[-1].period:
            worseIndex.append(i)
        else:
            g_statisticRes[i][1] += 1 
    min_val = min(lst)
    minIndex = []
    for i in range(len(lst)):
        if min_val == lst[i]:
            minIndex.append(i)
            g_statisticRes[i][3] += 1            
#    min_valInd = lst.index(min_val)    
    strLst = [dp.Etype2str(x,sDigit = 3) for x in lst]
    for i in worseIndex:
        strLst[i] = '\\textcolor{gray}{' + strLst[i] + '}'        
    for i in minIndex:
        strLst[i] = '\\textbf{' +strLst[i] + '}'
    resStr = str()
    for unit in strLst:
        resStr  += ' & ' + unit
    latexStr  += resStr        
    latexStr  += '\\'
    latexStr  += '\\'
    latexStr  += '\\'
    latexStr  += '\\'
    latexStr  += '\n'
    
    latexStr  += '\\hline\n'
    print(latexStr)
    return latexStr

def statistic2Latex(data,insNum):
#    for unit in data:
    str_statistic = str()
    for i in range(len(data) - 1):
        str_statistic += str(methodExdic[i])  + ' : '
        str_statistic += ' & ' + str(data[i][0]) + '('+ str(round((data[i][0]/insNum),2)) +')'
        str_statistic += ' & ' + str(data[i][1]) + '('+ str(round((data[i][1]/insNum),2)) +')'
        str_statistic += ' & ' + str(data[i][2]) + '('+ str(round((data[i][2]/insNum),2)) +')'
        str_statistic += ' & ' + str(data[i][3]) + '('+ str(round((data[i][3]/insNum),2)) +')'
        str_statistic += '\\'
        str_statistic += '\\'
        str_statistic  += '\n'
    return str_statistic                    

if __name__ == '__main__':
    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\\benchmark')
    dataPro = open('D:\py_code\MPDA_Preliminary\\benchmark\\comp_randPro.dat','w')         
    with open('D:\py_code\MPDA_Preliminary\\benchmark\\_randData.pk','rb') as f:
        randConData = pickle.load(f)
    fileIndex = 0
    randDict = dict()
    for file in files:
        tableDict = dict()
        
        if fileIndex > 2:
            break
        fileIndex += 1
        insName = root + '\\' + file
        tableDict['fileName'] = file
        
        pro = ins.Instance(insName)
        r1  = StaticConstructMethod(pro)
        _sol = r1.construct(cmpltReverse = True)
                
        r1Index = STATS_index(_sol.objective,r1._methodPeriod)

        r2 = StaticConstructMethod(pro)
        _sol = r2.construct(cmpltReverse = False)
        r2Index = STATS_index(_sol.objective,r2._methodPeriod)
        
        r3 = MinConstructMethodRT(pro)
        r3.reverse( reverse = False)
        vaild,_sol = r3.construct()
        r3Index = STATS_index(r3._opt_solution.objective,r3._methodPeriod)

        r4 = MinConstructMethodRT(pro)
        r4.reverse(reverse = True)
        vaild,_sol = r4.construct()
        r4Index = STATS_index(_sol.objective,r4._methodPeriod)

        
        tableDict['rand_per'] = randConData[file].period        
        tableDict['rand_ob'] = randConData[file].objective
        randIndex = STATS_index(randConData[file].objective,randConData[file].period)
        table_tuple = TableTuple(SR1 = r1Index,SR2 = r2Index,\
                                 MR1 = r3Index, MR2 = r4Index , Rand =  randIndex)
        
        dataPro.write(data2Latex(table_tuple,file))
    dataPro.close()
    print(g_statisticRes)
    dataPro = open('D:\py_code\MPDA_Preliminary\\benchmark\\STATS_randPro.dat','w')         
    dataPro.write(statistic2Latex(g_statisticRes,fileIndex))
    dataPro.close()
