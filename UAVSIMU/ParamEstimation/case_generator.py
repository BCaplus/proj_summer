# -*- coding: utf-8 -*-
# 飞行包线生成；扰动#


import matplotlib.pyplot as plt
from scipy import signal
from ControlEfficiencyModel import static_model
import xlrd
import random
import pandas as pd
import os




S = 4 # 最大截面面积 [m^2]
cd1 = 0.5 #平飞阻力系数 来自于文献
cd2 = 1.5 #90度俯仰角阻力系数
dry_weight = 40+20#干重，包括载荷但不包括电池 [kg]
max_fuel_mass = 12#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 900#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]
Height = 200 #定高飞行
Height_2nd = 700
theta = 5
max_P = 0

airdyn_param = [cd1, cd2]

# 飞行剖面的构成：某时刻飞行器的速度·高度和风速

# Flight类负责生成无人机模型，部署优化策略，并根据飞行剖面计算过程中变化和油耗

class Flight:
    def __init__(self, S, dry_weight, max_fuelmass, capacity, dt = 5):
        self.S = S
        self.cd1 = 0.4 #default
        self.cd2 = 1 #default
        self.dryweight = dry_weight
        self.max_fuel_mass = max_fuelmass
        self.capacity = capacity
        self.dt = dt
        self.T = 0
        self.n = 4
        self.time_sequence = [0]
        self.initial_SoC = 1

        # 机体参数
        self.plane_param = [4, 0.4, 1] #Parameters in [S cd1 cd2]

        # 旋翼参数
        self.prop_param = [5, 0.85, 0.75] #Parameters in [Dp, Hp, Bp]'

        # 电池电调参数
        self.bat_param = [172, 44, 1.65, 0.021] #Parameters in [kv0 Um0 Im0 Rm]
        self.ESC_param = [60, 0.01] #[Ue, Re]


    def set_dt(self, dt):
        self.dt = dt

    def set_initial_SoC(self, initSoC):
        self.initial_SoC = initSoC

    def set_initial_fuel(self, max_fuel):
        self.max_fuel_mass = max_fuel

    def set_capacity(self,capacity):
        self.capacity = capacity

    def load_profile(self, profile = []):
        if not profile:
            path = os.getcwd() + '\\profile.csv'
            f = open(path, encoding='utf-8')
            data = pd.read_csv(f)
            self.profile = data #格式：[t, h, u, v, flightmode, hfmode, wspeed]
        else:
            self.profile = profile


    def set_plane(self):
        raw = xlrd.open_workbook("plane_data.xls")
        sh = raw.sheet_by_name("Sheet1")
        for i in range(sh.nrows):
            row = [str(sh.cell_value(i, j)) for j in range(0, sh.ncols)]
            # 检查机体参数
            if "N_rotor" in row[0]:
                self.n = int(row[1])
            if "dry_weight" in row[0]:
                self.dryweight = float(row[1])
            if "Cd1" in row[0]:
                self.plane_param[1] = float(row[1])
            if "Cd2" in row[0]:
                self.plane_param[2] = float(row[1])
            if row[0] == 'S':
                # print(row)
                # print('S is'+row[1])
                self.plane_param[0] = float(row[1])
            if "number of rotors" in row[0]:
                self.n = int(float(row[1]))

            # 旋翼参数
            if "DP" in row[0]:
                self.prop_param[0] = float(row[1])
            if "HP" in row[0]:
                self.prop_param[1] = float(row[1])
            if "BP" in row[0]:
                self.prop_param[2] = float(row[1])
            # 电池电调参数
            if "kv0" in row[0]:
                self.bat_param[0] = float(row[1])
            if "Um0" in row[0]:
                self.bat_param[1] = float(row[1])
            if "Im0" in row[0]:
                self.bat_param[2] = float(row[1])
            if "Rm" in row[0]:
                self.bat_param[3] = float(row[1])
            if "Ue" in row[0]:
                self.ESC_param[0] = float(row[1])
            if "Re" in row[0]:
                self.ESC_param[1] = float(row[1])


        temp = static_model(self.plane_param[2], self.plane_param[0], self.plane_param[1], self.dryweight, self.max_fuel_mass, self.dt, self.capacity, self.ESC_param[0], n=self.n,SoC=self.initial_SoC)
        self.case = temp

    def simu_ECMS(self):
        # profile[index t h v u flightmode hfmode wspeed]
        for k in range(len(self.profile)):
            if self.profile[k][5] == 1:
                print("in case HF")
                self.case.set_flight_mode(self.profile[k][5])
                self.case.set_HF_mode(self.profile[k][6])
                self.case.set_wind(self.profile[k][7])
                self.case.set_u_ideal(self.profile[k][4])
                self.case.set_height(self.profile[k][2])

                self.case.update_ECMS(wind = 2)
                self.time_sequence.append(self.case.t)
                if 40<k<50:
                    print("selected; Preq is "+ str(self.case.powerSys.get_total_power()))
                    print("T is " + str(self.case.T))
                    print("Cd change " + str(self.case.fly.get_Cd()) + "Theta change "+str(self.case.fly.get_theta()))
            else:
                print('in case vertical h is ' + str(self.case.h))
                self.case.set_flight_mode(self.profile[k][5])
                self.case.set_wind(self.profile[k][7])
                self.case.set_vertical_speed(self.profile[k][3])
                self.case.set_height(self.profile[k][2])
                self.case.update_ECMS(wind = 2)
                self.time_sequence.append(self.case.t)

        print("fuel left "+ str(self.case.powerSys.get_fuelmass()))
        return self.case.get_flight_stat(), self.case.get_Bat_stat()

    def plot_flight_stat(self,flight_stat,t, t_excess = 50):
        plt.rcParams['savefig.dpi'] = 300

        plt.rcParams['figure.dpi'] = 300

        config = {
            "font.family": 'serif',
            "font.size": 16,
            "mathtext.fontset": 'stix',
            "font.serif": ['SimSun'],
        }

        SoC = [item[5] for item in flight_stat]
        P_need = [item[6] for item in flight_stat]
        P_GE = [item[7] for item in flight_stat]


        plt.figure(1)
        # plt.plot( Hf_t, miu_motor)
        plt.subplot(2, 1, 1)
        plt.plot(t, P_GE, label='PICE')
        # plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
        plt.plot(t, P_need, "red", label='Preq')
        plt.ylabel(r"PICE /W")
        plt.ylim(7500, 16000)
        plt.xlim(0, self.case.t + t_excess)
        plt.legend(loc=0, ncol=1, fontsize=14)
        plt.subplot(2, 1, 2)
        plt.plot(t, SoC, label='SoC')
        plt.ylabel('SoC')
        plt.xlabel('t /s')
        plt.ylim(0.1,1)
        plt.xlim(0, self.case.t + t_excess)
        plt.show()











    # def HFlight_by_T(self, end_T, caseNo = 0, wind = 0):
    #     while self.T<end_T:
    #
    #         if wind == 0:
    #             self.case[caseNo].FlightStat = 1
    #             self.case[caseNo].HFlightMode = 0
    #             self.updater(caseNo)
    #             for k in range(len(sub_case)):
    #                 self.case[sub_case[k]].FlightStat = 1
    #                 self.case[sub_case[k]].HFlightMode = 0
    #                 self.updater(sub_case[k])
    #
    #         else:
    #             self.updater(caseNo)
    #             w_speed = self.case[caseNo].get_wind_speed()
    #             for k in range(len(sub_case)):
    #                 self.case[sub_case[k]].set_wind_speed(w_speed)
    #                 self.updater(sub_case[k], wind = 1)


    # def plot_state(self):


class FlightProfileGenerator:
    def __init__(self,dt):
        self.dt = dt
        self.wind_counter = 0
        self.profile = [[0,0,0,0,0,0,0]] #[t h u v flightmode hfmode wspeed]
        self.wind_speed = 0

    def add_climb(self,escalation,time_period,w_on = 0, w = 12):
        u_set = escalation/time_period
        t_steps = int(time_period/self.dt)
        for i in range(t_steps):
            t = self.profile[len(self.profile)-1][0]
            t = t + self.dt
            h = self.profile[len(self.profile)-1][1]
            h = h + u_set * self.dt
            flightmode = 0 # 上升时为0 下降-1 平飞1
            u = u_set
            v = 0
            hfmode = 0
            if w_on:
                self.wind_speed_generator(w)#
                wspeed = self.wind_speed
                self.wind_counter += self.dt
            else:
                wspeed = 0
            self.profile.append([t,h,u,v,flightmode,hfmode,wspeed])




    def add_hflight(self,v,time_period,w_on = 0, w = 12):
        u = 0
        t_steps = int(time_period/self.dt)
        for i in range(t_steps):
            t = self.profile[len(self.profile)-1][0]
            t = t + self.dt
            h = self.profile[len(self.profile)-1][1]
            flightmode = 1
            v = v
            hfmode = 1
            if w_on:
                self.wind_speed_generator(w)#
                wspeed = self.wind_speed
                self.wind_counter += self.dt
            else:
                wspeed = 0
            self.profile.append([t, h, u, v, flightmode, hfmode, wspeed])


    def add_drop(self,drop_height,time_period,w_on = 0, w = 12):
        u_set = -drop_height/ time_period
        t_steps = int(time_period / self.dt)
        for i in range(t_steps):
            t = self.profile[len(self.profile) - 1][0]
            t = t + self.dt
            h = self.profile[len(self.profile) - 1][1]
            h = h + u_set * self.dt
            flightmode = -1  # 上升时为0 下降-1 平飞1
            u = u_set
            v = 0
            hfmode = 0
            if w_on:
                self.wind_speed_generator(w)#
                wspeed = self.wind_speed
                self.wind_counter += self.dt
            else:
                wspeed = 0
            self.profile.append([t, h, u, v, flightmode, hfmode, wspeed])


    def wind_speed_generator(self,average_windspeed, c_period = 40, mc_period = 240):
        average_wind = average_windspeed
        check_period = c_period
        max_change_periord = mc_period
        sigma = 1
        if self.wind_counter % check_period == 0 and self.wind_counter > 0:
            # print("check="+str(self.wind_counter%check_period))
            temp = (max_change_periord - self.wind_counter) / max_change_periord
            random_f = temp + random.random() * (1 - temp)
            if random_f > 0.5:
                self.wind_counter = 0
                temp = random.gauss(average_wind, sigma)
                temp = (temp - average_wind)*average_wind
                if temp > 1.2 * average_wind:
                    temp = 1.25*average_wind
                elif temp < -1.2 * average_wind:
                    temp = -1.25*average_wind
                self.wind_speed = temp



    def export_profile(self):
        outer = pd.DataFrame(data=self.profile)
        outer.to_csv("profile.csv")

    def plot_w_curve(self):
        t = [self.profile[i][0] for i in range(len(self.profile))]
        w = [self.profile[i][6] for i in range(len(self.profile))]
        print(w)
        plt.figure(2)
        plt.plot(t,w)
        plt.show()

# test = FlightProfileGenerator(5)
# test.add_climb(100,200,w_on=1,w=0)
# test.add_hflight(10,800,w_on=1,w=4)
# test.add_hflight(10,400,w_on=0)
# test.add_hflight(10,800,w_on=1,w=6)
# test.plot_w_curve()
# test.export_profile()

# test2 = Flight(4,63,12,900)
# test2.set_plane()
# print(test2.cd1)