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
    SR3 = 3
    MR1 = 4
    MR2 = 5
    MR3 = 6
methodExdic = dict()
methodExdic[0] = MethodType.SR1
methodExdic[1] = MethodType.SR2
methodExdic[2] = MethodType.SR3
methodExdic[3] = MethodType.MR1
methodExdic[4] = MethodType.MR2
methodExdic[5] = MethodType.MR3



TableTuple = collections.namedtuple('TableTuple',['SR0','SR1','SR2','OSR0','OSR1','OSR2','Rand'])
# =============================================================================
# the first means  the objective better than the random method
# the second means the calculation period better than the random alg
# the 3rd means the best objective in all methods\
# the 4th means the best calculation period in all methods
# =============================================================================
g_statisticRes =  []
for i in range(7):
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
    dataPro = open('D:\py_code\MPDA_Preliminary\\latexData\\comp_randPro.dat','w')         
    fileIndex = 0
    randDict = dict()
    benchmarkLst = []
    for file in files:
        str_file = file.split('_')        
        robNum = int(str_file[0])
        unit = (file,robNum)
        benchmarkLst.append(unit)
    benchmarkLst = sorted(benchmarkLst,key = lambda x: x[1])
#    print(benchmarkLst)
        
    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllRandData.pk','rb') as f:
        randConDataDic = pickle.load(f)

    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllStaticData.pk','rb') as f:
        SRConDataDic = pickle.load(f)

#    try:        
#    except:
#        print(wtf)
#        raise Exception('das')

    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllOneStaticData.pk','rb') as f:
        OSRConDataDic = pickle.load(f)
    
    
    print(benchmarkLst)
    print(len(benchmarkLst))
#    raise Exception('sad')       
#    print(SRConDataDic)
    
    ind = 0
    for unit in benchmarkLst:
#        tableDic = dict()
        fileName = unit[0]
        tableDic = file        
        print(ind)
        
        if ind % 26 == 0:
            dataPro.write('\\begin{table*}\n')
            dataPro.write('\\centering\n')
            dataPro.write('\\tiny\n')
            dataPro.write('\\begin{tabular}{cccccc|ccccccc}\n')
            dataPro.write('\\hline\n')
            dataPro.write('			robNum & taskNum & robPos & taskPos & robRate & taskRate  &SR1 &SR2 &SR1 &SR2 &MR1  &MR2 &RandCon \\\\ \n')            
        mean_randIndex = STATS_index(randConDataDic[fileName].mean_ob, randConDataDic[fileName].mean_peri)
        std_randIndex = STATS_index(randConDataDic[fileName].std_ob, randConDataDic[fileName].std_peri)
        
        SR0_ind  = STATS_index(SRConDataDic[fileName].minObjective0, SRConDataDic[fileName].period0)                
        SR1_ind  = STATS_index(SRConDataDic[fileName].minObjective1, SRConDataDic[fileName].period1)                
        SR2_ind  = STATS_index(SRConDataDic[fileName].minObjective2, SRConDataDic[fileName].period2)                

        OSR0_ind  = STATS_index(OSRConDataDic[fileName].minObjective0, OSRConDataDic[fileName].period0)                
        OSR1_ind  = STATS_index(OSRConDataDic[fileName].minObjective1, OSRConDataDic[fileName].period1)                
        OSR2_ind  = STATS_index(OSRConDataDic[fileName].minObjective2, OSRConDataDic[fileName].period2)                

        table_tuple = TableTuple(SR0 = SR0_ind, SR1 = SR1_ind,SR2 = SR2_ind\
                                 ,OSR0 = OSR0_ind, OSR1 = OSR1_ind, OSR2 = OSR2_ind , Rand =  mean_randIndex)
        dataPro.write(data2Latex(table_tuple,fileName))
        if ind %26 == 25:
            dataPro.write('\\end{tabular}\n')
            dataPro.write('\\end{table*}\n')
            dataPro.write('\n')
        ind += 1
        print(fileName)
    dataPro.write('\\end{tabular}\n')
    dataPro.write('\\end{table*}\n')
    dataPro.write('\n')
    dataPro.flush()

    
    print('dasd')
    raise Exception('sad')   
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
