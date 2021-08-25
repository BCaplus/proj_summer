# -*- coding: utf-8 -*-
# 根据片段的DP计算 #
# 简化计算，将发动机功率离散为[1,15kw]间的141个连续点，计算每个时间步上的总能量损失 #
# 损失函数：计算每个时间步上的总和能量浪费：电池上的充放电损失+（实际比油耗-最佳比油耗）*发动机功率*热值#
# 然而，可能出现损失函数最小的策略消耗燃料较多的情形，因为无法控制开始时的电量#
# 采用从后往前的算法，末态油量=0.5kg,soc=0.3，可以算出总的功率需求，将末态的发动机功率同样离散，根据多个#
# 状态空间：发动机功率P，认为从末态反推到任意一个时刻上的某个发动机功率点的总损失函数的最小值对应了最优策略#

# 画图用 暂时空着
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# 计算用
from ControlEfficiencyModel import static_model
from case_generator import Flight
import pandas as pd
import os

# 读剖面
def profile_reader():
    path = os.getcwd() + '\profile.csv'
    print('step1 done')
    profile = pd.read_csv(path)
    print('step2 done')
    profile = profile.values.tolist()
    print('step3 done')
    return profile

class DP_calculator:
    def __init__(self,profile,case):
        # self.initState = [] #[SoC, Fuel, P_egn]
        # self.endState = []
        self.case = case
        self.profile = profile
        self.PSearchRange = [2,2]
        self.k = len(self.profile)

        # 离散状态空间写在这里
        self.PLowerBound  = 1 #kW
        self.PUpperBound = 15 #kW
        self.nDiscrt = 141
        self.PInterval = (self.PUpperBound - self.PLowerBound)/(self.nDiscrt  - 1)

        # 离散SoC
        self.SoCLowerBound = 0
        self.SoCUpperBound = 1
        self.mDiscrt = 1001
        self.SoCInterval = (self.SoCUpperBound - self.SoCLowerBound)/(self.mDiscrt - 1)
        # 设计离散时取整除，因此这里不做截断误差检查

        self.initialization()

    def set_final_state(self,SoC, Fuelmass):
        # self.endStat = [SoC, Fuel, P_egn] #已统一格式
        self.Fmass[self.k-1] = [Fuelmass for i in range(self.nDiscrt)]
        self.SoC[self.k - 1] = [SoC for i in range(self.nDiscrt)]

    def set_P_search_range(self,range):
        self.PSearchRange = range

    def set_NO_of_discetized_P(self, n):
        self.nDiscrt = n

    # 初始化
    def initialization(self):
        self.Fmass = [[[0 for m in range(self.mDiscrt)] for i in range(self.nDiscrt)]for j in range(self.k)]
        self.costF = [[-1 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.SoC = [[self.SoCLowerBound + i*self.SoCInterval for i in range(self.mDiscrt)]for j in range(self.k)]
        self.PEngine = [[self.PLowerBound + i*self.PInterval for i in range(self.nDiscrt)]for j in range(self.k)]
        self.costF[self.k - 1] = [0 for i in range(self.nDiscrt)]
        print("state space initialized")
        # 为变化的末态P预留的空间
        # self.
    # 设定初态SoC
    def set_initial_values_of_SoC(self, initial_SoC):
        self.SoC[self.k - 1] = [initial_SoC for i in range(self.nDiscrt)]

    def DP_PandSoC_as_state_var(self):
        # 逆向计算
        for k in range(self.k-1,0,-1):
            self.step_to_step_calculator_P_and_SoC_state_var(k)
        # 遍历寻找初态最低的Fmass
        outer = pd.DataFrame(data=self.SoC)
        outer.to_csv("SoC.csv")
        outer = pd.DataFrame(data=self.costF)
        outer.to_csv("cF.csv")
        minFC_index = -1  # 防空
        minFC = 100  # 初始
        for n in range(self.nDiscrt):
            if 0<self.Fmass[0][n]<minFC:
                minFC_index = n
                minFC = self.Fmass[0][n]
        return [minFC_index, minFC]

    # def DP_P_SoC_as_state_var(self):
    #     # 逆向计算
    #     for k in range(self.k):
    #         self

    def step_to_step_calculator_P_and_SoC_state_var(self, k): #k的定义：时间点对应的列表索引 而非逻辑索引
        #读取当前风速等信息
        if k == 0:
            print("out of boundary")
        elif k == 1:
            # K的边界检查在本方法的外部进行
            wspeed = self.profile[k - 1][6]
            self.case.set_wind(wspeed)
            # 读入上一个时间步的飞行条件，profile[t h u v flightmode hfmode wspeed]
            hfMode = self.profile[k-1][5]
            flightMode = self.profile[k-1][4]
            u_expect = self.profile[k-1][2]
            v_expect = self.profile[k-1][3]
            # h 好像是多余的
            # 传递给模型
            self.case.HFlightMode = hfMode
            self.case.flight_stat = flightMode
            self.case.set_u_ideal(u_expect)
            self.case.set_vertical_speed(v_expect)
            # 计算
            self.init_state_sticker(k)
        else:
            # K的边界检查在本方法的外部进行
            wspeed = self.profile[k - 1][6]
            self.case.set_wind(wspeed)
            # 读入上一个时间步的飞行条件
            hfMode = self.profile[k-1][5]
            flightMode = self.profile[k-1][4]
            u_expect = self.profile[k - 1][2]
            v_expect = self.profile[k - 1][3]
            # 传递变量
            self.case.HFlightMode = hfMode
            self.case.flight_stat = flightMode
            self.case.set_u_ideal(u_expect)
            self.case.set_vertical_speed(v_expect)
            # 计算
            self.StateUpdater_P_and_SoC_state_var(k)
            # print(self.SoC[k])
            # print(self.costF[k-1])

    def StateUpdater_P_and_SoC_state_var(self,k):
        # 计算两个状态间的油量、SoC变化在ControlEffMod里进行,n是功率点的索引序号（0~140),k是当前的时间步数
        # 后向计算
        # 从状态空间中的每个状态点依次向前更新,状态空间是二维的
        for StatusIndex in range(self.nDiscrt):
            if self.costF[k][StatusIndex] != -1: #检查当前时间点状态点有效性
                # print("in")
                #确定搜索域 边界：（1）不超过发动机输出边界 （2）不使Pbat超过电池功率边界 （3）SoC不低于0（可以大于1，矫正即可） 由于总需求功率在状态量循环层未知，（2）（3）在计算层检查
                fowardStat = [self.Fmass[k][StatusIndex], self.PEngine[k][StatusIndex], self.SoC[k][StatusIndex],
                              self.costF[k][StatusIndex]]
                for PengineIndex in range(self.nDiscrt):
                    prePengine = self.PEngine[k - 1][PengineIndex]
                    # 生成Stat，格式[Fmass, Pengine, SoC, costF]

                    backwardStat = self.case.sectional_compt(fowardStat,prePengine,self.profile[k-1],k) #暂时没有迭代
                    # 更新前向点

                    if backwardStat[3] != -1: #检查本次计算结果有没有意义
                        if self.costF[k - 1][PengineIndex] == -1:
                            # if PengineIndex%10 == 0:
                            # print('init cF case')
                            self.costF[k - 1][PengineIndex] = backwardStat[3]
                            self.Fmass[k - 1][PengineIndex] = backwardStat[0]
                            self.SoC[k - 1][PengineIndex] = backwardStat[2]
                        else:

                            if backwardStat[3] < self.costF[k - 1][PengineIndex]:
                            # 替换
                            #     if PengineIndex % 10 == 0:
                            #         print('swap case')
                                self.Fmass[k - 1][PengineIndex] = backwardStat[0]
                                self.SoC[k - 1][PengineIndex] = backwardStat[2]
                                self.costF[k - 1][PengineIndex] = backwardStat[3]


                            # print('swap case NEW CF IS ' + str(self.costF[k - 1][PengineIndex]))
                            # print(self.costF[k - 1])

        print("finished step: "+str(k)+"current SoC is /n")
        print(self.SoC[k - 1])
        # --print(self.Fmass[k-1])

    def init_state_sticker(self,k):
        if k!=1:
            print("wrong call")
        else:
            for StateIndex in range(self.nDiscrt):
                if self.costF[k][StateIndex] != -1:

                    for PengineIndex in range(self.nDiscrt):
                        prePengine = self.PEngine[k - 1][PengineIndex]
                        fowardStat = [self.Fmass[k][StateIndex], self.PEngine[k][StateIndex],
                                      self.SoC[k][StateIndex], self.costF[k][StateIndex]]
                        backwardStat = self.case.sectional_compt(fowardStat, prePengine, self.profile[k - 1], k)# 暂时没有迭代 迭代的话也写在这里面
                        if backwardStat[3] != -1 and  backwardStat[2] > 0:
                            self.Fmass[k - 1][PengineIndex] = backwardStat[0]
                            self.SoC[k - 1][PengineIndex] = backwardStat[2]
                            self.costF[k - 1][PengineIndex] = backwardStat[3]



    # def StateUpdater_P_SoC_var(self,k):
    #
    #     # 在本层进行状态循环和吸附
    #     for PIndex in range(self.nDiscrt):
    #         for SoCIndex in range(self.mDiscrt):
    #             if self.


# 测试

S = 4 # 最大截面面积 [m^2]
cd1 = 0.5 #平飞阻力系数 来自于文献
cd2 = 1.5 #90度俯仰角阻力系数
dry_weight = 40+23#干重，包括载荷但不包括电池 [kg]
max_fuel_mass = 12#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 900#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]
Height = 200 #定高飞行
Height_2nd = 700
theta = 5
t = [0]
max_P = 0

flight = Flight(S,dry_weight,max_fuel_mass,capacity,dt = dt)
flight.set_plane()
print('--rotyor number is' + str(flight.case.n))

profile = profile_reader()
# print(profile)
test = DP_calculator(profile,flight.case)
test.set_NO_of_discetized_P(141)
# test.set_initial_values_of_SoC(0.3)
test.set_final_state(0.3,0)
result = test.DP_P_as_state_var()
print(result)
print()

