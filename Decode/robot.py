# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:50:30 2018

@author: robot
"""

import numpy as np
import math
from enum import Enum

class RobotState(Enum):
    onRoad = 1
    onTask = 2


class Robot():
    def __init__(self):
        self.arriveTime = 0
        self.leaveTime = 0
        self.executeDur = 0
        self.roadDur = 0
        self.encodeIndex = 0
        self.taskID = -1
        self.stateType =  RobotState['onRoad']  
        self.stopBool = False
        self.executeBool = False        
        self.ability = 0
        self.vel = 0
    def display(self):
        print(' arriveTime ',self.arriveTime,' leaveTime ',self.leaveTime,
        ' executeDur', self.executeDur,' roadDur',self.roadDur,
        ' encodeIndex ',self.encodeIndex, ' taskID ',self.taskID,
        ' stateType ', self.stateType, ' stopBool ',self.stopBool,
        ' excuteBool ',self.executeBool,' ability ',self.ability,
        'vel',self.vel)        
    
        

        
if __name__ == '__main__':
    rob = Robot()
    rob.display()
    