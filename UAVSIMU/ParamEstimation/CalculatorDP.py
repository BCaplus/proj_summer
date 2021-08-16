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
        self.nDiscrt = 141
        self.k = len(self.profile)

    def set_final_state(self,SoC, Fuel, P_egn):
        self.endState = [SoC, Fuel, P_egn]

    def set_P_search_range(self,range):
        self.PSearchRange = range

    def set_NO_of_discetized_P(self, n):
        self.nDiscrt = n

    # 初始化
    def initialization(self):
        self.FCmass = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.costF = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.SoC = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        self.PEngine = [[0 for i in range(self.nDiscrt)]for j in range(self.k)]
        # 为变化的末态P预留的空间
        # self.

    def set_initial_values_of_SoC(self, initial_SoC):

    def DP(self):
        for k in range(self.k):
            for n in range(self.nDiscrt):
                self.StepSearcher(n)

    def step_to_step_calculator(self, ancestorStat, decentStat, k): #k的定义：时间点对应的列表索引 而非逻辑索引
        #读取当前风速等信息
        wspeed = self.profile.[k-1][6]
        # K的边界检查在本方法的外部进行
        self.case.set_wind(wspeed)
        #
        hfMode = self.profile[k-1][5]
        flightMode = self.profile[k-1][4]
        self.case.
    def StepSearcher(self,n,k):
        # 计算两个状态间的油量、SoC变化在ControlEffMod里进行,n是功率点的索引序号（0~140),k是当前的时间步数
        # 后向计算
        P_n = 1+n*14*(self.nDiscrt - 1)
        temp = 14/(self.nDiscrt - 1)
        if P_n - self.PSearchRange[0]>1:
            lowerBound = P_n - self.PSearchRange[0]
        else:
            lowerBound = 1

        if P_n + self.PSearchRange[0]<15:
            upperBound = P_n - self.PSearchRange[0]
        else:
            upperBound = 15
        n_search = int((upperBound - lowerBound)/temp) #上探下探均为正数
        acents = [(lowerBound + i*temp) for i in range(n_search+1)]
        Pf_present = self.PEngine[k][n]
        for candidate in acents:
            # 生成Stat，格式[Fmass, Pengine, SoC, costF]
            decentStat = [self.FCmass, self.PEngine, self.SoC, self.costF]
            acentStat = [0, candidate, self.SoC, self.costF]
            self.





