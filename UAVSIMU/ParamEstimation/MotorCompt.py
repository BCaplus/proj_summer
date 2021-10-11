#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import math

class Motor:
    # Kv0, Um0, Im0, Rm, Gm
    Motor_Param = [172, 44, 1.65, 0.021, 3.46]

    def __init__(self, M=0, N=0, Param = Motor_Param):
        self.M = M
        self.N = N
        self.kv0 = Param[0]
        self.Um0 = Param[1]
        self.Im0 = Param[2]
        self.Rm = Param[3]
        self.Gm = Param[4]
        self.Im = 0
        self.Um = 0
        self.MotorElec()



    def MotorElec(self):
        temp = self.kv0*self.Um0/(self.Um0 - self.Im0*self.Rm)
        self.Im = temp*self.M/9.55 + self.Im0
        self.Um = self.Im*self.Rm + self.N/temp
        #print([temp, self.Um, self.Im])

    def MotorMechanic(self):
        temp = self.kv0 * self.Um0 / (self.Um0 - self.Im0 * self.Rm)

        self.M = (self.Im - self.Im0)*9.55/temp
        self.N = (self.Um - self.Im*self.Rm)*temp
        #print([temp, self.M, self.N])

    def get_MotorWeight(self):
        return self.Gm

    def update(self, M, N):
        self.M = M
        self.N = N
        self.MotorElec()

    def update_progressive(self, Um, Im):
        self.Um = Um
        self.Im = Im
        self.MotorMechanic()

    def get_Um(self):
        return self.Um

    def get_Im(self):
        return self.Im

    def get_M(self):
        return self.M

    def get_N(self):
        return self.N

    def get_MotorP(self):
        return self.Im*self.Um

class ESC:
    # IeMax, Re, Ge, Ub(电调输出电压), Rb（电调等效内阻）
    ESC_Param = [30, 0.021, 0.25, 60, 0.01]
    # 旋翼数

    def __init__(self, Um = [], Im = [], Param = ESC_Param, n = 6):
        self.Um = Um
        self.Im = Im
        self.IeMax = Param[0]
        self.Re = Param[1]
        self.Ge = Param[2]
        self.Ub = Param[3]
        self.Rb = Param[4]
        self.Throttle = [0 for i in range(n)]
        self.Ie = [0 for i in range(n)]
        self.Ie_net = 0
        self.Ue = 0
        self.n = 6

    def ThrottleCalc(self):
        for i in range(self.n):
            self.Throttle[i] = (self.Um[i] + self.Im[i]*self.Re)/self.Ub

    def ESCelec(self):
        # 飞行器辅助部件耗电
        I_ext = 1

        for i in range(self.n):
            self.Ie[i] = self.Throttle[i]*self.Im[i]

        self.Ie_net = sum(self.Ie)
        #print(self.Ie_net)
        self.Ue = self.Ub - (self.Ie_net + I_ext)*self.Rb

    def ESCprogressive(self, Unet, Inet):
        #print(Inet)
        I_ext = 1
        self.U_m_net = self.Ub - Inet*self.Re
        self.I_m_net = Inet - I_ext
        self.I_m = self.I_m_net/n
        return [self.U_m_net, self.I_m]


    def update(self, Um = [], Im = []):
        self.Um = Um
        self.Im = Im
        self.ThrottleCalc()
        self.ESCelec()

    def get_ESC_U(self):
        return self.Ue

    def get_ESC_I(self):
        return self.Ie_net

    def get_ESC_power(self):
        return self.Ie_net*self.Ue

    def get_ESC_weight(self):
        return self.n*self.Ge

    def set_Ub(self, Ub):
        self.Ub = Ub
