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

ResData = collections.namedtuple('ResData',['objective','period'])

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

if __name__ == '__main__':
    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\\benchmark')
    fileIndex = 0
    randDict = dict()
    open('D:\py_code\MPDA_Preliminary\\benchmark\\_randDataTest.pk','wb')         
    for file in files:
        if fileIndex > 30:
            break
        fileIndex += 1
        insName = root + '\\' + file
        pro = ins.Instance(insName)
        print(pro)
        con = RandConstructMethod(pro)
        start = time.clock()
        _sol = con.construct()
        end = time.clock()
        period = end -start
        print('CalPeriod = ', )        
        randDict[file] = ResData(objective = _sol.objective, period = period)
    print(randDict)
    with open('D:\py_code\MPDA_Preliminary\\benchmark\\_randDataTest.pk','wb') as f:
        pickle.dump(randDict,f, pickle.HIGHEST_PROTOCOL)
    wtfData = dict()
    with open('D:\py_code\MPDA_Preliminary\\benchmark\\_randDataTest.pk','rb') as f:
        wtfData = pickle.load(f)
    print('wtf',wtfData)

