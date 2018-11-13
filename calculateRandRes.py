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

ResData = collections.namedtuple('ResData',['fileName','minObjective',\
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
        if fileIndex > endInd:
            break
        fileIndex += 1
        print('ind = ',fileIndex,' has been cmplted')        
        if fileIndex <= beginInd:
            continue
        insName = root + '\\' + file
        pro = ins.Instance(insName)
        print(pro)        
        con = RandConstructMethod(pro)
#        start = time.clock()
        _sol = con.construct(sampleTimes = 1000)
#        end = time.clock()
#        period = end -start
        with open('D:\py_code\MPDA_Preliminary\\STATS_data\\_randDataTest' + str(beginInd) + '_' + str(endInd) +'.pk',\
                  'ab') as pk_file:         
            pickle.dump(ResData(fileName = file, minObjective = _sol.objective, period = con._methodPeriod,\
                                meanObjective = con._meanObjective,stdObjective = con._stdObjective,vaildRate = con._vaildRate),pk_file)
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
    
        
#        randDict[file] = ResData(objective = _sol.objective, period = period)
#    print(randDict)
#    with open('D:\py_code\MPDA_Preliminary\\benchmark\\_randDataTest80-100.pk','wb') as f:
#        pickle.dump(randDict,f, pickle.HIGHEST_PROTOCOL)
#    wtfData = dict()
#    with open('D:\py_code\MPDA_Preliminary\\benchmark\\_randDataTest80-100.pk','rb') as f:
#        wtfData = pickle.load(f)
#    print('wtf',wtfData)



#   print ('输入的文件为：', inputfile)
#   print ('输出的文件为：', outputfile)



if __name__ == '__main__':
    main(sys.argv[1:])

