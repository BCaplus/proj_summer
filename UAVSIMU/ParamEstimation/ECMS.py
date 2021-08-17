#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import math
import numpy as np
from OptimumFuelTrajectory import OptimumFC

class BatteryEC:
    def __init__(self, Rdis, Rchrg, Vbat, Pavrg, C_avg, beta = 0.3):#注意Pavrg是电池的平均功率
        self.Rdis = Rdis
        self.Rchrg = Rchrg
        self.Vbat = Vbat
        self.Pavrg = Pavrg
        self.avgDisEff = 0.5*(1 + math.sqrt(1 - 4*self.Rdis*Pavrg/self.Vbat**2))
        self.avgChrgEff = 2/(1 + math.sqrt(1 - 4*self.Rchrg*Pavrg/self.Vbat**2))
        self.C_avg = C_avg
        self.SoCH = 0.4
        self.SoCL = 0.2
        self.beta = beta

    def get_ModifiedEquiBC(self, SoC, Pbat, mode):
        Cbat = self.__equivalentBC(Pbat, mode)
        aveSoC = 0.5*(self.SoCH + self.SoCL)
        delta_SoC = 2*(SoC - aveSoC)/(self.SoCH - self.SoCL)
        return (1 - self.beta*delta_SoC)*Cbat

    def calcDisEff(self, Pdis):
        #print(Pdis)
        temp = 1 - 4*self.Rdis*Pdis/self.Vbat**2
        temp = math.sqrt(temp)
        return 0.5*(1 + temp)

    def calcChrgEff(self, Pchrg):
        temp = 1 - 4*self.Rchrg*Pchrg/self.Vbat**2
        temp = math.sqrt(temp)
        return 2/(1 + temp)

    def __equivalentBC(self, Pbat, mode):
        # 0为充电 1为放电
        if mode == 0:
            eta_dis = self.calcDisEff(Pbat)
            temp = self.C_avg*self.avgChrgEff*Pbat/eta_dis
        else:
            eta_chrg = self.calcChrgEff(Pbat)
            temp = self.C_avg*Pbat/(eta_chrg*self.avgChrgEff)
        return temp


class FuelManagement:

    B_param = [0.09, 0.09, 60, 2000, 375] #Rdis, Rchrg, Vbat, Pavg, C_avg(g/h)

    def __init__(self, param = [1,15.8], ave_n = 100):
        self.lower_P = param[0]
        self.upper_P = param[1]
        self.__SoC = 1
        self.__fuelMass = 0
        self.__powerDemand = 0
        self.__P_interval = 0.1 #kW
        self.__fuelcomsup = OptimumFC()
        self.__fuelcomsup.import_map_bycol()
        self.OptF = 0
        #self.ave_Pice = [0 for ]
        print("FM set")

    def update_fuel_mass(self, fuelmass):
        self.__fuelMass = fuelmass

    def update_SoC(self, SoC):
        self.__SoC = SoC

    def update_power_demand(self,PDemand):
        self.__powerDemand = PDemand


    def set_Battery(self, param = B_param):
        self.Bat = BatteryEC(param[0], param[1], param[2], param[3], param[4] )

    def opt_search(self, Pem):
        temp = self.__fuelcomsup.get_Opt_FC_DOUBLE_Interp(Pem)
        return temp

    def get_min_reduced_FC(self):
        return self.__fuelcomsup.get_min_reduced_FC()

    def split(self, pnet, search_range = [1, 15.8]):

        Pnet = pnet/1000
        m = int((search_range[1] - search_range[0])/self.__P_interval) + 3
        P_spc = np.linspace(search_range[0], search_range[1], m)
        P_ice = 1
        P_em = 0
        F_min = 100000 # g/hr
        F = F_min
        F_monitor = []
        for p_ice in range(m):
            if P_spc[p_ice] > Pnet:
                mode = 0
            else:
                mode = 1
            rate = self.__fuelcomsup.get_Opt_FC(P_spc[p_ice])
            F_ICE = rate*P_spc[p_ice]
            F_E = self.Bat.get_ModifiedEquiBC(self.__SoC, Pnet - P_spc[p_ice], mode)
            F_net = F_ICE + F_E
            F_monitor.append([F_ICE, F_E, P_spc, rate])
            if F_net < F_min:
                F = F_ICE
                F_min = F_net
                P_ice = P_spc[p_ice]
                P_em = Pnet - P_spc[p_ice]
        if P_ice<5:
            print("low p_ice " +str([P_ice, search_range[0],search_range[1], Pnet]))
            print(F_monitor)
        print([F_ICE, F_E])
        return [F, P_ice, P_em]

    def split_test(self):
        Pnet = 11
        m = int((self.upper_P - self.lower_P) / self.__P_interval)
        P_spc = np.linspace(self.lower_P, self.upper_P, m)
        P_ice = 0
        P_em = 0
        F_min = 10000  # g/hr
        SoC = 0.2
        P_ice1 = 8
        F_ICE1 = self.__fuelcomsup.get_Opt_FC(  P_ice1) * P_ice1
        F_E1 = self.Bat.get_ModifiedEquiBC(SoC, Pnet - P_ice1, 1)