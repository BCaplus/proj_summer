#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import math
from PropellerCompt import PropellerComputation
from MotorCompt import Motor, ESC
from HorizontalandVerticalFlight import FlyParam
from SeriesPowerSys import SHPS
import random

#模拟参数
local_g = 9.81 #当地重力加速度

Gp = 0.01 #旋翼重量 （没什么用）

# 发电系统map

class static_model:

    def __init__(self, S, cd1, cd2, dry_weight, MaxFuelMass, dt, capacity, Ub, max_ge_power = 15000,EnergyDensity = 300,  n = 6, SoC = 1, local_g = 9.81, theta = 0, tem = 20):
        self.S = S
        self.cd1 = cd1
        self.cd2 = cd2
        self.g = local_g
        self.theta = theta/180*math.pi
        self.n = n #旋翼数
        self.dry_weight = dry_weight + capacity/EnergyDensity
        self.dt = dt
        self.Capacity = capacity # Wh
        self.total_weight = MaxFuelMass + self.dry_weight
        self.T = self.total_weight*self.g/math.cos(self.theta)
        # 电机电调
        self.motor = Motor()
        self.ESC = ESC()


        # 飞行/环境状态
        self.fly = FlyParam(theta)
        self.fly.set_cd(self.cd1,self.cd2)
        self.u = 0 #水平速度
        self.u_ideal = 0 #期望水平速度
        self.theta_ideal = 0 #期望俯仰角
        self.v = 0 #垂直速度
        self.h = 0 #海拔
        self.l = 0 #飞行距离
        self.tmprtr = tem #摄氏度
        self.HFlightMode = 0 #水平飞行模式 默认定角
        self.FlightStat = 0 #飞行姿态，爬升(0)平飞（1）下降（2）

        # 推进器
        self.rho = 0
        self.__update_rho()
        self.prop = PropellerComputation(self.T, 0.01, self.rho)
        # 动力系统
        self.powerSys = SHPS(Ub, MaxFuelMass, SoC, self.dt,self.Capacity)
        self.max_ge_power = max_ge_power
        self.Ub = Ub
        # 定速飞行时俯仰角速度
        self.q = 0

        # 飞行时间、距离
        self.t = 0
        self.distance = 0

        # 功率跟踪
        self.p_prev = 12000

        # 模拟突风计时器
        self.wind_counter = 0
        self.wind_speed = 0

        # 监视器
        self.flight_stat = [[0, 0, MaxFuelMass, 0, 0, 1, 0, 0]] # u,v,fuelmass,distance,h,soc,P_demand,P_ICE_output
        self.Bat_stat = [[0, 0]]


    def __update_rho(self):
        temp = 1 - 0.0065 * self.h / (273 + self.tmprtr)
        Pa = 101325 * math.pow(temp, 5.2561)
        self.rho = 273 * Pa * 1.293 / (101325 * 273 + self.tmprtr)


    def update_weight(self):
        self.total_weight = self.powerSys.get_fuelmass() + self.dry_weight
        #print(self.powerSys.get_fuelmass())

    def update_T(self):
        Cd = self.fly.get_Cd()
        F_d = 0.5 * Cd * self.rho * (self.v + self.wind_speed) ** 2 * self.S
        if self.FlightStat == 1:
            temp = self.total_weight * self.g / math.cos(self.theta)
            r = temp**2 + F_d**2
            self.T = math.sqrt(r)

        elif self.FlightStat == 0:


            self.T = F_d + self.total_weight*self.g
        else:


            self.T = -F_d + self.total_weight * self.g
        #print([self.T, self.v])

    def update_propeller(self):
        self.__update_rho()
        self.prop.update(self.T/self.n, self.rho)
    def set_wind(self,windspeed):
        self.wind_speed = windspeed


    def update_motor(self):
        M = self.prop.get_M()
        N = self.prop.get_N()
        self.motor.update(M, N)
        #print(self.motor.get_MotorP())
        Im = [self.motor.get_Im() for i in range(self.n)]
        Um = [self.motor.get_Um() for i in range(self.n)]
        self.ESC.update(Um, Im)

    def calc_motor(self):

        temp = self.ESC.ESCprogressive(self.Ub, self.powerSys.get_Iout())
        print(self.powerSys.get_Iout())
        print(temp)
        self.motor.update_progressive(temp[0],temp[1])
        self.motor.MotorMechanic()

    def calc_propeller(self):
        self.__update_rho()
        self.prop.update_progressive(self.motor.get_M(), self.motor.get_N(), self.rho)
        self.T = self.prop.get_T()*self.n

    def calc_theta_u(self):
        self.theta = math.acos(self.total_weight * self.g/(self.prop.get_T()*self.n))
        Cd = self.fly.get_Cd()
        F_d = self.T - self.total_weight * self.g
        self.u = math.sqrt(F_d/ (0.5 * Cd * self.rho * self.S))

    def calc_v(self):
        Cd = self.fly.get_Cd()
        F_d = self.total_weight * self.g - self.T
        if F_d > 0:
            self.v = math.sqrt(F_d/ (0.5 * Cd * self.rho * self.S))
        else:
            self.v = -math.sqrt(-F_d / (0.5 * Cd * self.rho * self.S))

    def update_powersys_RULE(self):
        self.powerSys.update_RULE(self.ESC.get_ESC_I())

    def update_powersys_ECMS(self):
        self.powerSys.A_ECMS(self.ESC.get_ESC_I())

    def calc_powersys_ECMS(self, P):
        #print(P)
        self.powerSys.A_ECMS(P/self.Ub)
        self.p_prev = self.Ub*self.powerSys.get_Iout()

    def update_flight(self):
        self.fly.set_theta(self.theta)
        if self.FlightStat == 1:
            self.u = self.fly.get_Velo(self.rho, self.total_weight*self.g, self.S)
            self.v = 0
        else:
            self.u = 0

    def flight_track(self, u_exp, v_exp):
        k1 = 0.001
        k2 = 0.001

        diff = k1*(v_exp - self.h)*abs(v_exp - self.v) + k2*(u_exp - self.u)*abs(u_exp - self.u)
        P_exp = self.p_prev + diff
        return P_exp


    def set_vertical_speed(self, v):
        self.v = v

    def update_theta(self):
        alpha = 0.002
        beta = 0.002
        if self.FlightStat == 1:
            if self.powerSys.stat == 0:
                self.theta = self.theta + self.dt*self.q  #此处单位为°
            else :
                self.theta = self.theta + alpha*(self.powerSys.get_Iout() - self.ESC.get_ESC_I()) - beta
        else:
            self.theta = 0
        #print([self.theta*180/math.pi, self.powerSys.stat, 6*self.motor.get_MotorP(), self.powerSys.get_soc(), self.powerSys.get_fuelmass(),self.powerSys.Ige,self.rho])


    def VeloOrientedFlight(self):
        Cd = self.fly.get_Cd()
        # p控制系数
        P = 0.05

        tan_ideal_theta = self.u_ideal**2*self.rho*self.S*Cd/(2*self.total_weight*self.g)
        ideal_theta = math.atan(tan_ideal_theta)
        self.q = P*(ideal_theta - self.theta)

    def set_u_ideal(self, u_ideal):
        self.u_ideal = u_ideal

    def ConstantThetaFlight(self):
        # p控制系数
        P = 0.05
        self.q = P * (self.theta_ideal - self.theta)
        #print(self.q)

    def set_ideal_theta(self, theta):
        self.theta_ideal = theta/180*math.pi

    def get_ESC_efficiency(self):
        temp = self.n*self.motor.get_MotorP()/self.powerSys.get_total_power()
        return temp

    def get_FC_by_P(self,P):
        return self.powerSys.get_optFC_P(P)

    def get_Motor_efficiency(self):
        temp = self.prop.get_P()/self.motor.get_MotorP()
        return temp

    def set_T(self, T):
        self.T = T

    def update(self,wind = 0, mode = 0, T_out = 0):
        self.__update_rho()
        self.update_weight()
        if wind == 0:
            self.wind_cease()
        if mode == 0:
            self.update_T()
        else:
            self.set_T(T_out)
        self.update_propeller()
        self.update_motor()
        self.update_powersys_RULE()
        self.update_flight()
        self.update_theta()

        if self.FlightStat == 1:
            if self.HFlightMode  == 1:
                self.VeloOrientedFlight()
            else:
                self.ConstantThetaFlight()
        else:
            self.h += self.v*self.dt
        self.t = self.t + self.dt
        self.distance = self.distance + self.u * self.dt
        self.flight_stat.append(
            [self.u, self.v, self.powerSys.fuelMass, self.distance,self.h, self.powerSys.SoC,
             self.ESC.get_ESC_power(),self.powerSys.get_ge_power()])
        self.Bat_stat.append([self.powerSys.get_Bat_heat(), self.powerSys.get_I_bat()])

        print("rule+"+str([self.T,self.theta]))

    def update_ECMS(self,wind = 0):
        self.__update_rho()
        self.update_weight()
        if wind == 1:
            self.combined_wind(10)
        elif wind == 0:
            self.wind_cease()
        self.update_T()
        self.update_propeller()
        self.update_motor()
        self.update_powersys_ECMS()
        self.update_flight()
        self.update_theta()
        if self.FlightStat == 1:
            if self.HFlightMode == 1:
                self.VeloOrientedFlight()
            else:
                self.ConstantThetaFlight()
        else:
            self.h += self.v * self.dt
        self.t = self.t + self.dt
        self.distance = self.distance + self.u * self.dt
        # print([self.theta, self.T,self.wind_speed])

        self.flight_stat.append(
            [self.u, self.v, self.powerSys.fuelMass, self.distance, self.h, self.powerSys.SoC,
             self.ESC.get_ESC_power(), self.powerSys.get_ge_power()])
        self.Bat_stat.append([self.powerSys.get_Bat_heat(), self.powerSys.get_I_bat()])

        print("ecms+" + str([self.T, self.theta]))

    def update_ECMS_dynamic(self, u, v, flight_mode):
        self.__update_rho()
        self.update_weight()
        P_exp = self.flight_track(u,v)
        self.calc_powersys_ECMS(P_exp)
        self.calc_motor()
        self.calc_propeller()
        if self.FlightStat == 1:
            self.calc_theta_u()
        else:
            self.calc_v()
        #print([self.v, self.total_weight * self.g - self.T, self.p_prev, self.T, self.prop.get_T(), self.motor.get_M()*self.motor.get_N(), self.motor.get_Um(), self.motor.get_Im()])
        self.h += self.v * self.dt
        self.t = self.t + self.dt
        self.distance = self.distance + self.u * self.dt


    def combined_wind(self, wx):
        average_wind = wx
        check_period = 80
        max_change_periord = 1000
        sigma = 5
        if self.wind_counter%check_period == 0 and self.wind_counter>0:
            #print("check="+str(self.wind_counter%check_period))
            temp = (max_change_periord - self.wind_counter)/max_change_periord
            random_f = temp + random.random()*(1-temp)
            if random_f > 0.5:
                self.wind_counter = 0
                temp = random.gauss(average_wind, sigma)
                temp = temp - average_wind
                if temp>1.2*wx:
                    temp = wx
                self.wind_speed = temp
        else:
            self.wind_counter+=self.dt


    def sectional_compt(self, initial_state, Pengine_backward, profile, k, recur = 5):
        # profile的格式：[t h u v flightmode hfmode wspeed]

        #测试时手动设置，也可来自于发动机运行曲线搜索
        # 燃料热值
        Hfuel = 44000000 #汽油,J/kg
        Hf_coefficient  = Hfuel #暂时不调参

        minFC = self.powerSys.ecms.get_min_reduced_FC()
        # stat的格式[Fmass, Pengine, SoC, costF]
        wspeed = profile[6]
        self.set_wind(wspeed)
        hfMode = int(self.profile[5])
        flightMode = int(self.profile[4]) #取值 0：上升或下降（取决于v的值） 1：平飞
        Fmass_initial = initial_state[0]
        weight_initial = initial_state[0]+self.dry_weight
        SoC_initial = initial_state[2]
        costF_initial = initial_state[3]
        self.total_weight = weight_initial
        self.FlightStat = flightMode
        self.update_T()
        self.u = profile[2]
        self.v = profile[3]
        self.update_propeller()
        self.update_motor()
        Pengine = Pengine_backward
        P_req = self.ESC.get_ESC_power()
        P_bat = P_req - Pengine
        max_P_bat = self.powerSys.Ibmax * self.powerSys.Ub / 1000 #单位是kW
        # 检查搜索可行性应该在外部做 这里进行一个电池最大功率的保险和SoC越界的检查
        # SoC可用性应该在外面做
        if abs(P_bat)<max_P_bat:
            # 如果不离散SoC,无需迭代；否则recur得到上一步的状态点
            # for i in range(recur):
            #     #迭代求SoC
            wfuel, reducedFC = self.get_FC_by_P(Pengine) #还需要查比油耗
            weight_backward = weight_initial + wfuel*self.dt #单位为kg【待检查】
            Fmass_backward = Fmass_initial + wfuel*self.dt
            SoC_backward = SoC_initial - P_bat*self.dt*1000/(self.powerSys.Ub*self.powerSys.capacity) #capacity单位[A*s]
            # SoC可用性检查
            if SoC_backward > 0:
                Ub = self.Ub #电池电压 同时也当开路电压用 假装有个效率1的变压器
                Rb = self.powerSys.ecms.Bat.Rdis
                sqrt = math.sqrt(Ub*Ub - 4*Rb*P_bat)
                BatteryDissipation = 0.5*Ub*Ub/Rb - 0.5*Ub*sqrt/Rb - P_bat
                costF_backward = costF_initial + BatteryDissipation*self.dt + (reducedFC - minFC)*Hfuel*Pengine*self.dt #[待检查]
                if SoC_backward > 1:
                    # 充电溢出能量
                    costF_backward = costF_backward + (SoC_backward - 1)*self.Capacity*3600
                    # 校正
                    SoC_backward = 1
            else:
                costF_backward = -1  # 用-1表示不可到达（在更新时也要检查，注意costF原本为负时可以用新的正值来覆盖）
                SoC_backward = -1
                Fmass_backward = -1
                Pengine = Pengine_backward
        else:
            costF_backward = -1 #用-1表示不可到达（在更新时也要检查，注意costF原本为负时可以用新的正值来覆盖）
            SoC_backward = -1
            Fmass_backward = -1
            Pengine = Pengine_backward

        return [Fmass_backward,Pengine_backward,SoC_backward,costF_backward]
        # 暂且写成这样

    def get_wind_speed(self):
        return self.wind_speed

    def wind_cease(self):
        self.wind_speed = 0
        self.wind_counter = 0

    def get_flight_stat(self):
        return self.flight_stat

    def get_Bat_stat(self):
        return self.Bat_stat

    def get_fuel_C(self):
        return self.powerSys.get_fuel_C()

    def get_fuel_reduced_C(self):
        return self.powerSys.get_fuel_reduced_C()

    def get_eff_elec(self):
        return 6*self.prop.get_P()/self.powerSys.get_total_power()