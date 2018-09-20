# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 20:07:19 2018

@author: robot
"""

def change2EType(x):
    if x== 0:
        return 0
    else:
        base =  0.1 **10
        basePower = - 10
        while True:
            num =  x /base
            if num < 9.999999999999993:
#                print(num)
                break
            basePower = basePower + 1
            base = base *10
        return basePower
    
#significance digit  = sDigit
'''
只能计算有效数字大于等于2的
不能计算十分接近9.999999999999993的数字
'''
def Etype2str(x,sDigit = 4):
    v_num  = change2EType(x)
    xx = x/(10**v_num)    
    str_0 = str()
    i_xx = int(round(round(xx,sDigit - 1)*10**(sDigit-1)))
#    print(round(xx,sDigit - 1)*100)
    for i in range(sDigit - 2):
#        print(i_xx)
        if i_xx%10 ==  0:
            str_0 += '0'
#            print('str_0 = ',str_0)
            i_xx /= 10
            i_xx = int(i_xx)
        else:
            break
    str_x =  str(round(xx,sDigit - 1))    
    if(v_num >= 0):
        str_x = str_x + str_0 +'E+'+str(v_num) 
    else:
        str_x = str_x + str_0 +'E'+str(v_num) 
    return str_x

if __name__ == '__main__':
    print(Etype2str(9.997,3))
    print(round(1,3))
