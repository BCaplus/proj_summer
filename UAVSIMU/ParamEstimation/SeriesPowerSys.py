#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import math
from ECMS import FuelManagement, OptimumFC

class SHPS:
    # Igmax最大发电机输出, Gshps, capacity电池容量, BalanceR, lowestR, MaxR, Iop, Imin发电机最小输出, Ibmax电池最大输出
    HSPS_Param = [245, 16, 60000, 0.3, 0.6, 183, 1, 60]
    "series hybrid power system"
    def __init__(self, Ub, InitFuelMass, SoC, dt, capacity, Param = HSPS_Param):
        self.Ub = Ub
        self.Imax = Param[0]
        self.Gshps = Param[1]
        self.capacity = capacity*3600/Ub #转换后单位 [As]
        self.SoC = SoC
        self.fuelMass = InitFuelMass
        self.dt = dt
        self.blcR = 270/capacity
        self.maxR = min(540/capacity,1)
        self.Iop = Param[5]
        self.Imin = Param[6]
        self.Ige = 0
        self.Ib_out = 0
        self.Ibmax = Param[7]
        self.Iout = 0
        self.stat = 0 #0正常工作，1输出不足
        self.stable_counter = 0
        self.ecms = FuelManagement()
        self.ecms.set_Battery()
        self.FC = 0 # 实时总油耗
        self.reduced_FC = 0 #实时比油耗

    def Map(self, U, I):
        # p = U*I
        # rate = 0.00015
        # if p>self.Iop*self.Ub:
        #     wfuel = p*(p/(self.Iop*self.Ub))*rate/1000
        # else:
        #     wfuel = p*rate/1000
        # #print(wfuel)
        FC = self.ecms.opt_search(U*I/1000)
        self.reduced_FC = FC
        #print(FC)
        wfuel = FC*(U*I/1000)/3600000
        self.FC = wfuel
        return wfuel

    def get_optFC_P(self,P): #注意，P的单位是kW
        FC = self.ecms.opt_search(P)/1000 #单位是kg
        wfuel = FC*P/3600 #单位是kg/s
        return wfuel, FC

    def ECMS_RULE(self, Ib):

        if Ib <= self.Ibmax + self.Imax :
            if self.stable_counter == 0:
                if self.SoC  >= self.maxR:
                    if Ib <= self.Ibmax + self.Imin:
                        self.Wfuel = self.Map(self.Ub, self.Imin)
                        self.Ib_out = Ib - self.Imin
                        self.Ige = self.Imin
                    else:
                        self.Wfuel = self.Map(self.Ub, Ib - self.Ibmax)
                        self.Ib_out = self.Ibmax
                        self.Ige = Ib - self.Ibmax
                    self.stat = 0
                    self.stable_counter = 10
                elif self.SoC  >= self.blcR:
                    if Ib <= self.Ibmax + self.Iop:
                        self.Wfuel = self.Map(self.Ub, self.Iop)
                        self.Ib_out = Ib - self.Iop
                        self.Ige = self.Iop
                    else :
                        self.Wfuel = self.Map(self.Ub, Ib - self.Ibmax)
                        self.Ib_out = self.Ibmax
                        self.Ige = Ib - self.Ibmax
                    self.stat = 0
                    self.stable_counter = 10
                else:
                    if self.Iop > Ib:
                        self.Wfuel = self.Map(self.Ub, self.Iop)
                        self.Ib_out = Ib - self.Iop
                        self.Ige = self.Iop
                        self.stat = 0
                        self.stable_counter = 10
                    elif self.Imax > Ib:
                        self.Wfuel = self.Map(self.Ub, self.Imax)
                        self.Ib_out = Ib - self.Imax
                        self.Ige = self.Imax
                        self.stat = 0
                        self.stable_counter = 10
                    else:
                        self.Wfuel = self.Map(self.Ub, self.Imax)
                        if self.SoC * self.capacity >= (Ib - self.Imax) * self.dt:
                            self.Ib_out = Ib - self.Imax
                        else:
                            self.Ib_out = 0
                        self.Ige = self.Imax
                        self.stat = 1
                        self.stable_counter = 0
            else:
                self.stable_counter -= 1


        else:
            if self.SoC*self.capacity >= self.Ibmax*self.dt:
                self.Wfuel = self.Map(self.Ub, self.Imax)
                self.Ib_out = self.Ibmax
                self.Ige = self.Imax
            else :
                self.Wfuel = self.Map(self.Ub, self.Imax)
                self.Ib_out = 0
                self.Ige = self.Imax
            self.stat = 1
            self.stable_counter = 0

        self.Iout = self.Ige + self.Ib_out

    def update_RULE(self, Ib):
        self.ECMS_RULE(Ib)
        self.fuelMass = self.fuelMass - self.Wfuel*self.dt

        self.SoC = self.SoC - self.Ib_out * self.dt/self.capacity
        #print(self.SoC)


    def A_ECMS(self, I_net):
        I_prev = self.Ige
        Pnet = I_net*self.Ub
        P_upper = (I_prev*self.Ub + 300)/1000
        if P_upper > 15.8:
            P_upper = 15.8
        P_lower = (I_prev*self.Ub - 800)/1000
        if P_lower< Pnet/1000 - 3:
            P_lower = Pnet/1000 - 3
        if P_upper<= P_lower:
            P_upper = P_lower + 0.6


        self.ecms.update_SoC(self.SoC)
        self.ecms.update_fuel_mass(self.fuelMass)
        self.ecms.update_power_demand(Pnet)
        temp = self.ecms.split(Pnet, search_range = [P_lower, P_upper])
        self.fuelMass = self.fuelMass - temp[0] * self.dt/3600000
        self.SoC = self.SoC - temp[2]*1000 * self.dt / (self.capacity * self.Ub)
        self.Iout = I_net
        #print(I_net)
        self.Ige = temp[1]*1000/self.Ub
        self.Ib_out = I_net - self.Ige
        #print([P_lower, P_upper, Pnet, self.Ige*self.Ub/1000])
        self.FC = temp[0] /3600000
        self.reduced_FC = temp[0]/temp[1]

    def get_weight(self):
        return self.fuelMass + self.Gshps

    def get_fuelmass(self):
        return self.fuelMass

    def get_Iout(self):
        return self.Iout

    def get_soc(self):
        return self.SoC

    def get_ge_power(self):
        return self.Ige*self.Ub

    def get_total_power(self):
        return self.Iout*self.Ub

    def get_I_bat(self):
        return self.Ib_out

    def get_Bat_heat(self):
        return self.ecms.Bat.Rdis*self.dt*self.Ib_out**2

    def get_fuel_C(self):
        return self.FC

    def get_fuel_reduced_C(self):
        return self.reduced_FC




