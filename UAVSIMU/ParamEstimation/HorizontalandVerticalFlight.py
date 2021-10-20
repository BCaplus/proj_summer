#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import math

class FlyParam:
    #velo and propeller force T
    #Cd1, Cd2
    Flight_Param = [3,1.5]

    def __init__(self, theta, Param = Flight_Param):
        self.theta = theta
        self.cd1 = Param[0]
        self.cd2 = Param[1]
        self.Cd = self.cd1*(1 - math.sin(self.theta)**3) + self.cd2*(1 - math.cos(self.theta)**3)

    def get_Velo(self, rho, G, S):
        self.Cd = self.cd1 * (1 - math.sin(self.theta) ** 3) + self.cd2 * (1 - math.cos(self.theta) ** 3)
        temp = 2*G*math.tan(self.theta)/(rho*S*self.Cd)
        velo = math.sqrt(temp)
        return velo

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta

    def get_Cd(self):
        return self.Cd

    def set_cd(self, cd1, cd2):
        self.cd1 = cd1
        self.cd2 = cd2

