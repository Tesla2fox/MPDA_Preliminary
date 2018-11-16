# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 09:24:16 2018

@author: robot
"""

#import constructMethod as randCon
from constructMethod import *
import os
import pickle
import time
import collections
import sys, getopt
import numpy as np

ResData = collections.namedtuple('ResData',['fileName','minObjective','evaluateNum',\
                                            'period','meanObjective','stdObjective','vaildRate'])
RandDataPK = collections.namedtuple('RandDataPK',['mean_ob','std_ob','min_ob','mean_peri','std_peri'\
                                                  ,'mean_eNum','std_eNum'])


def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
        pass
#        print('root is ',root) #当前目录路径  
#        print('dirs are ',dirs) #当前路径下所有子目录  
#        print('files are',files) #当前路径下所有非目录子文件
    return root,dirs,files

'''
In string, the \b \n  has another meaning,  so we should write it in the \\benchmark
'''

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hb:e:",["begin=","end="])
    except getopt.GetoptError:
        print ('error test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
        print(opts)   
    for opt, arg in opts:
        if opt == '-h':
            print ('help calculatedRandRes.py -begin <inputfile> -end <outputfile>')
            sys.exit()
        elif opt in ("-b", "--begin"):
            beginInd = int(arg)
        elif opt in ("-e", "--end"):
            endInd = int(arg)

    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\\benchmark')
    fileIndex = 0
#    randDict = dict()    
    pk_file = open('D:\py_code\MPDA_Preliminary\\STATS_data\\_randDataTest' + str(beginInd) + '_' + str(endInd) +'.pk'\
         ,'wb')
    pk_file.close()         
    for file in files:
        if fileIndex >= endInd:
            break
        fileIndex += 1
        if fileIndex <= beginInd:
            continue
        print('ind = ',fileIndex,' has been cmplted')        
        insName = root + '\\' + file
        pro = ins.Instance(insName)
#        print(pro)        
#        for i in range(10):
        for i in range(20):            
            con = RandConstructMethod(pro)
#        start = time.clock()
            _sol = con.construct()
#        end = time.clock()
#        period = end -start
        
            with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_randDataTest' + str(beginInd) + '_' + str(endInd) +'.pk',\
                      'ab') as pk_file:         
                pickle.dump(ResData(fileName = file, minObjective = _sol.objective , evaluateNum = con._evaluateNum,period = con._methodPeriod,\
                                    meanObjective = 0,stdObjective = 0,vaildRate = 0),pk_file)
                pk_file.close()    
        print('success')
#    pk_file = open("test.dat",'rb')

    pk_file = open("D:\py_code\MPDA_Preliminary\\STATS_data\\_randDataTest" + str(beginInd) + "_" + str(endInd) +".pk",\
                'rb')
    while True:
        try:
            wtf = pickle.load(pk_file)
        except Exception as e:
            print(e)
            break
        print(wtf)
    pk_file.close()
    
def processData():
    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\\STATS_data\\_rand')
    dic = dict()
    for file in files:
        print(file)
        pk_file = open(root + '\\' + file,'rb')
        while True:
            try:
                data = pickle.load(pk_file)
                
            except Exception as e:
                print(e)
                break
            if data.fileName in dic:                
                dic[data.fileName].append(data)
            else:
                dic[data.fileName] = []
                dic[data.fileName].append(data)
#            print(wtf)
        pk_file.close()
        
    pickDic = dict()
    for key in dic:
        ob_lst = []
        peri_lst = []
        eNum_lst = []
        for unit in dic[key]:
            ob_lst.append(unit.minObjective)
            peri_lst.append(unit.period)
            eNum_lst.append(unit.evaluateNum)
        ob_arry = np.array(ob_lst)
        mean_ob = np.mean(ob_arry)
        std_ob = np.std(ob_arry)
        min_ob = min(ob_lst)
#        min_ob = np.min(ob_arry) 
        
        peri_arry = np.array(peri_lst)
        mean_peri = np.mean(peri_arry)
        std_peri = np.std(peri_arry)

        eNum_arry = np.array(eNum_lst)
        mean_eNum = np.mean(eNum_arry)
        std_eNum = np.std(eNum_arry)
        
        pickDic[key] = RandDataPK(mean_ob = mean_ob,std_ob = std_ob,min_ob = min_ob,\
                                  mean_peri = mean_peri, std_peri = std_peri,
                                  mean_eNum = mean_eNum, std_eNum = std_eNum)
        
#    print('pickDic',pickDic)        

    pk_file = open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllRandData' +'.pk','wb')
    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllRandData' +'.pk',\
              'ab') as pk_file:         
                pickle.dump(pickDic,pk_file)
                pk_file.close()
    pk_file = open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllRandData' +'.pk','rb')
    p  =  pickle.load(pk_file)
#    print('p',p)

#    print(dic)

        
if __name__ == '__main__':
#    main(sys.argv[1:])
    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllStaticData.pk','rb') as f:
        SRConDataDic = pickle.load(f)
    print(SRConDataDic)
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')    
    processData()
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_AllStaticData.pk','rb') as f:
        SRConDataDic = pickle.load(f)
    print(SRConDataDic)

