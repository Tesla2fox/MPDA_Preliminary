# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 20:57:35 2018

@author: robot
"""

import Decode.decode as dc
import random
import time
import dataProcess.dataProcess as dp



    
def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
        print(root) #当前目录路径  
        print(dirs) #当前路径下所有子目录  
        print(files) #当前路径下所有非目录子文件
    return root,dirs,files


def data2Latex(dic = dict()):
    print(dic)
    latexStr = str()
    latexStr += str(dic['robNum'])
    latexStr += ' & '
    latexStr += str(dic['taskNum'])

    latexStr += ' & '
    latexStr += dp.Etype2str(dic['rc_ms'],sDigit = 3)
    latexStr += ' & '
    latexStr += dp.Etype2str(dic['ss_ms'],sDigit = 3)    
    latexStr += ' & '
    latexStr += dp.Etype2str(dic['nb_ms_c'],sDigit = 3)
    latexStr += ' & '
    latexStr += dp.Etype2str(dic['nb_ms'],sDigit = 3)

    if dic['rc_calDur'] < dic['ss_calDur']:
        latexStr += ' & '
        latexStr +='\\textbf{'
        latexStr += dp.Etype2str(dic['rc_calDur'],sDigit = 3)
        latexStr += '}'
        latexStr += ' & '
        latexStr += dp.Etype2str(dic['ss_calDur'],sDigit = 3)
    else:
        latexStr += ' & '
        latexStr += dp.Etype2str(dic['rc_calDur'],sDigit = 3)
        latexStr += ' & '
        latexStr +='\\textbf{'
        latexStr += dp.Etype2str(dic['ss_calDur'],sDigit = 3)
        latexStr += '}'
            
    latexStr += ' & '
    latexStr += dp.Etype2str(dic['nb_calDur_c'],sDigit = 3)
    latexStr += ' & '
    latexStr += dp.Etype2str(dic['nb_calDur'],sDigit = 3)
        
    latexStr += '\\'
    latexStr += '\\'
    
    return latexStr
if __name__ == '__main__':
    
    dataPro = open('.\\debug\\dataPro.dat','w')         

    root,dirs,files = file_name('D:\py_code\MPDA_Preliminary\data')
    
    fileIndex = 0
    for file in files:
        
        if fileIndex > 12:
            break        
        fileIndex += 1
        if fileIndex <= 8:
            continue
        insName = root+'\\' + file
        print(insName)
        d_rc = dc.DecodeRC(insName)    
        d_ss = dc.DecodeSS(insName)
        d_nb = dc.DecodeNB(insName)
        robNum = d_rc.robNum
        taskNum = d_rc.taskNum
#        print(robNum)
#        print(taskNum)
        for i in range(10):
            dic = dict()
            dic['robNum'] = robNum
            dic['taskNum'] = taskNum
            random.seed(i)
            d_nb.generateRandEncode()
#            d_nb.saveEncode()
            start = time.clock()
            makespan = d_nb.decode()
            end = time.clock()
            print('newDecodeTime = ', end - start)
            print('nb_makespan = ',makespan)
            dic['nb_calDur'] = end- start
            dic['nb_ms'] = makespan
            
            random.seed(i)
            d_rc.generateRandEncode()
#            d_rc.saveEncode()
            start = time.clock()
            makespan = d_rc.decode()
            end = time.clock()
            print('newDecodeTime = ', end - start)
            print('rc_makespan = ',makespan)
            dic['rc_calDur'] = end- start
            dic['rc_ms'] = makespan


            random.seed(i)    
            d_ss.generateRandEncode()
#            d_ss.saveEncode()
            start = time.clock()
            makespan = d_ss.decode()
            end = time.clock()
            print('newDecodeTime = ', end - start)
            print('ss_makespan = ',makespan)
            dic['ss_calDur'] = end- start
            dic['ss_ms'] = makespan

                        
            encode = d_ss.genNoBacktrackEncode()
            d_nb.encode = encode
            start = time.clock()            
            makespan = d_nb.decode()
            end = time.clock()
            print('newDecodeTime = ', end - start)
            print('newNb_makespan = ',makespan)
            dic['nb_calDur_c'] = end- start
            dic['nb_ms_c'] = makespan
            latexStr = data2Latex(dic)
            dataPro.write(latexStr+'\n')
            dataPro.flush()
            print(dic)
        dataPro.write('\\hline\n')
        d_rc.endDeg()
        d_ss.endDeg()
        d_nb.endDeg()        
#        break
    dataPro.close()
#        dc.
                
        