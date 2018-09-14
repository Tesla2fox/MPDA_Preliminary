# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 09:18:24 2018

@author: robot
"""


import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import random
from numpy import *
from copy import *
import copy
from readCfg.read_cfg import Read_Cfg
from IPython.display import HTML,display 
import colorlover as cl

#import read_cfg 

class Pnt:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    def pnt2dict(self):
        dic = dict(x = x,y= y)
        return dic
    def display(self):
        print('x = ',self.x,'y = ',self.y)

class Circle:
    def __init__(self,pnt = Pnt(),rad = 0):
        self.x = pnt.x
        self.y = pnt.y
        self.rad = rad
        self.x0 = self.x  - self.rad
        self.y0 = self.y  - self.rad
        self.x1 = self.x  + self.rad
        self.y1 = self.y  + self.rad
    def circle2dict(self):
        dic = dict()
        dic['type'] = 'circle'
        dic['xref'] = 'x'
        dic['yref'] = 'y'
        dic['x0'] = self.x0
        dic['y0'] = self.y0
        dic['x1'] = self.x1
        dic['y1'] = self.y1        
        dic['line'] = dict(color = 'rgba(50, 171, 96, 1)')
        return dic
class Line:
    def __init__(self,pnt0 =Pnt(),pnt1=Pnt()):
        self.x0 = pnt0.x
        self.y0 = pnt0.y
        self.x1 = pnt1.x
        self.y1 = pnt1.y
    def line2dict(self):
        dic= dict()
        dic['type']='line'
        dic['x0'] =self.x0
        dic['y0'] =self.y0
        dic['x1'] =self.x1
        dic['y1'] =self.y1
        dic['line'] = dict(color = 'rgb(128, 0, 128)')
        return dic
class Rect:
    def __init__(self,pnt =Pnt(),width =0,height =0):
        self.x0 = pnt.x
        self.y0 = pnt.y
        self.x1 = self.x0 + width
        self.y1 = self.y0 + height
    def rect2dict(self):
        dic = dict()
        dic['type']='rect'
        dic['x0'] = self.x0
        dic['y0'] = self.y0
        dic['x1'] = self.x1
        dic['y1'] = self.y1
        dic['line'] = dict(color = 'rgb(128, 0, 128)')
        return dic

class Pic:
    def __init__(self):
        self.shapeLst = []
        self.drawData = []
        self.annotations=  []
    def addRob(self,rob_x = [],rob_y =[]):
        for i in range(len(rob_x)):
            startTrace = go.Scatter(x =[rob_x[i]], y = [rob_y[i]],mode ='markers',
                                    marker = dict(symbol = 'cross-dot',size = 20),
                                    name = 
#                                    'start')
                                    'Robot_'+ str(i))
            self.drawData.append(startTrace)
    def addTsk(self,tsk_x = [], tsk_y = []):
        for i in range(len(tsk_x)):
            startTrace = go.Scatter(x =[tsk_x[i]], y = [tsk_y[i]],mode ='markers',
                                    marker = dict(symbol = 'circle-open-dot',size = 20),
                                    name = 
#                                    'start')
                                    'Task_'+ str(i))
            self.drawData.append(startTrace)        
    def drawPic(self,name = './pic/env',fileType = True,cordRange = 100):
        layout = {}
        
        layout['xaxis'] = dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        autotick=True,
        ticks='',
        showticklabels = False)
#        layout['xaxis']['range'] = [0,cordRange]
        layout['yaxis'] =dict(
        scaleanchor = "x",        
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        autotick=True,
        ticks='',
        showticklabels = False)
        layout['legend'] =   dict(font=dict(
            family='sans-serif',
            size=25,
            color='#000'
        ))
#        layout['yaxis']['range'] = [0,cordRange]
        fig = dict(data = self.drawData ,layout = layout)
        if(fileType):
            plotly.offline.plot(fig,filename = name + '.html',validate=False)
        else:
            py.image.save_as(fig,filename = name+'.jpeg')
def drawPic(insFileName = './data//s100_8_10_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.txt'):
    py.sign_in('tesla_fox', 'HOTRQ3nIOdYUUszDIfgN')
    readCfg = Read_Cfg(insFileName)
    ins_pic  = Pic()
    robNum = int(readCfg.getSingleVal('robNum')) 

    rob_x = []
    readCfg.get('rob_x',rob_x)
    rob_y = []
    readCfg.get('rob_y',rob_y)
    print('begin')    
    ins_pic.addRob(rob_x,rob_y)

    tsk_x = []
    readCfg.get('tsk_x',tsk_x)
    tsk_y = []
    readCfg.get('tsk_y',tsk_y)
    ins_pic.addTsk(tsk_x,tsk_y)    
    ins_pic.drawPic(name = './pic/env'+'test',fileType = True)
        

if __name__ == '__main__':
    insFileName = './data//s100_8_10_max100_2.5_1.2_1.2_1.2_thre0.1_MPDAins.txt'
    drawPic(insFileName)
    
    
    
    
    
    
    