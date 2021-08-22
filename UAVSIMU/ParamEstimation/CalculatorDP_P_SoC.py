# -*- coding: utf-8 -*-
# 根据片段的DP计算 #
# 简化计算，将发动机功率离散为[1,15kw]间的141个连续点，计算每个时间步上的总能量损失 #
# 损失函数：计算每个时间步上的总和能量浪费：电池上的充放电损失+（实际比油耗-最佳比油耗）*发动机功率*热值#
# 然而，可能出现损失函数最小的策略消耗燃料较多的情形，因为无法控制开始时的电量#
# 采用从后往前的算法，末态油量=0.5kg,soc=0.3，可以算出总的功率需求，将末态的发动机功率同样离散，根据多个#
# 状态空间：发动机功率P，认为从末态反推到任意一个时刻上的某个发动机功率点的总损失函数的最小值对应了最优策略#

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from ControlEfficiencyModel import static_model
import xlrd
import random
import pandas as pd
import os

def profile_reader():
    path = os.getcwd() + 'profile.csv'
    profile = pd.read_csv(path)
    profile = profile.values.tolist()
    return profile

class DP_calculator:
    def __init__(self,profile,case = static_model(0,0,0,0,0,00,00,0)):
        self.initState = [] #[SoC, Fuel, P_egn]
        self.endState = []
        self.case = case
        self.profile = profile
        # self.PenaltyFunction = [[]]
        # self.FuelComsumption = [[]]
        # self.SoC = [[]]
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

    def set_final_state(self,SoC, Fuel, P_egn):
        self.endStat = [SoC, Fuel, P_egn] #已统一格式

    def set_P_search_range(self,range):
        self.PSearchRange = range

    def set_NO_of_discetized_P(self, n):
        self.nDiscrt = n

    # 初始化
    def initialization(self):
        self.Fmass = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.costF = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.SoC = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.PEngine = [[self.PLowerBound + i*self.PInterval for i in range(self.nDiscrt)]for j in range(self.k)]
        # 为变化的末态P预留的空间
        # self.
    # 设定初态SoC
    def set_initial_values_of_SoC(self, initial_SoC):
        self.SoC[self.k - 1] = [initial_SoC for i in range(self.nDiscrt)]

    def DP_P_as_state_var(self):
        # 逆向计算
        for k in range(self.k):
            self.step_to_step_calculator(k)
        # 遍历寻找初态最低的Fmass

    def DP_P_SoC_as_state_var(self):
        # 逆向计算
        for k in range(self.k):
            self

    def step_to_step_calculator_P_state_var(self, k): #k的定义：时间点对应的列表索引 而非逻辑索引
        #读取当前风速等信息
        if k == 0:
            print("out of boundary")
        else:
            # K的边界检查在本方法的外部进行
            wspeed = self.profile[k - 1][6]
            self.case.set_wind(wspeed)
            # 读入上一个时间步的飞行条件
            hfMode = self.profile[k-1][5]
            flightMode = self.profile[k-1][4]
            u_expect = self.profile[k-1][]
            self.case.HFlightMode = hfMode
            self.case.flight_stat = flightMode
            self.StatusUpdater(k)

    def StateUpdater_P_state_var(self,k):
        # 计算两个状态间的油量、SoC变化在ControlEffMod里进行,n是功率点的索引序号（0~140),k是当前的时间步数
        # 后向计算
        # 从状态空间中的每个状态点依次向前更新
        for StatusIndex in range(self.nDiscrt):
            if self.costF[k][StatusIndex] != -1: #检查当前时间点状态点有效性
                #确定搜索域 边界：（1）不超过发动机输出边界 （2）不使Pbat超过电池功率边界 （3）SoC不低于0（可以大于1，矫正即可） 由于总需求功率在状态量循环层未知，（2）（3）在计算层检查

                for PengineIndex in range(self.nDiscrt):
                    prePengine = self.PEngine[k][PengineIndex]
                    # 生成Stat，格式[Fmass, Pengine, SoC, costF]
                    fowardStat = [self.Fmass, self.PEngine, self.SoC, self.costF]
                    backwardStat = self.case.sectional_compt(fowardStat,prePengine,k) #暂时没有迭代
                    # 更新前向点
                    if backwardStat[3] != -1: #检查本次计算结果有没有意义
                        if backwardStat[3] < self.costF[k][PengineIndex]:
                            # 替换
                            self.Fmass[k][PengineIndex] = backwardStat[0]
                            self.SoC[k][PengineIndex] = backwardStat[2]
                            self.costF[k][PengineIndex] = backwardStat[3]

    def StateUpdater_P_SoC_var(self,k):

        # 在本层进行状态循环和吸附
        for PIndex in range(self.nDiscrt):
            for SoCIndex in range(self.mDiscrt):
                if self.





