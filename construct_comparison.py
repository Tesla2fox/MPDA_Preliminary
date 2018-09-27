# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 14:50:12 2018

@author: robot
"""

import os
import random
import time
import dataProcess.dataProcess as dp
#import ins
import constructMethod as cm
#import sys
#import constructMethod.solution as sol

print(sys.path)

def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
        print(root) #当前目录路径  
        print(dirs) #当前路径下所有子目录  
        print(files) #当前路径下所有非目录子文件
    return root,dirs,files

if __name__ == '__main__':    
    dataPro = open('.\\debug\\dataPro.dat','w')         
    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\data')    
    fileIndex = 0
    for file in files:
        if fileIndex > 0:
            break
        insName =  root + '\\' + file
#        insName = 's100_3_4_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.dat'
        insPro = cm.Instance(insName)
#        ins.Instance(insName)
        sol_pro = cm.sol.Solution(insPro)
#        print(sol_pro)
#        print(insPro)
        fileIndex  += 1
#        rCon.
        r_con = cm.RandConstructMethod(insPro)
        r_sol = r_con.construct(sampleTimes = 100)
        print(r_sol)
        s_con = cm.sCon.StaticConstructMethod(insPro)
        s1_sol = s_con.construct(cmpltReverse = False)
        print(s1_sol)
        s2_sol = s_con.construct(cmpltReverse = True)
        print(s2_sol)
        
#        con = StaticConstructMethod(pro)