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

ResData = collections.namedtuple('ResData',['fileName','minObjective','evaluateNum',\
                                            'period','meanObjective','stdObjective','vaildRate'])

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
    
        
if __name__ == '__main__':
    main(sys.argv[1:])

