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
import copy

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

class DP_calculator_withSoC:
    def __init__(self,profile,case):
        # self.initState = [] #[SoC, Fuel, P_egn]
        # self.endState = []
        self.case = case
        self.temp_case = copy.deepcopy(case)
        self.profile = profile
        out_profile = pd.DataFrame(data=self.profile)
        out_profile.to_csv("readProfile.csv")
        print("profile format")
        print(self.profile[2])
        self.PSearchRange = [2,2]
        self.k = len(self.profile)
        self.PbMax = self.case.get_PbMax()

        # 离散状态空间写在这里
        self.PLowerBound  = 1 #kW
        self.PUpperBound = 15 #kW
        self.nDiscrt = 71
        self.PInterval = (self.PUpperBound - self.PLowerBound)/(self.nDiscrt  - 1)

        # 离散SoC
        self.SoCLowerBound = 0
        self.SoCUpperBound = 1
        self.mDiscrt = 1251
        self.SoCInterval = (self.SoCUpperBound - self.SoCLowerBound)/(self.mDiscrt - 1)
        # 设计离散时取整除，因此这里不做截断误差检查


        #调试参数
        self.SoC_max_increase_sequence=[]

        #初始化
        self.initialization()



    # def set_final_state(self,SoC, Fuelmass):
    #     # self.endStat = [SoC, Fuel, P_egn] #已统一格式
    #     self.Fmass[self.k-1] = [Fuelmass for i in range(self.nDiscrt)]
    #     self.SoC[self.k - 1] = [SoC for i in range(self.nDiscrt)]

    def set_P_search_range(self,range):
        self.PSearchRange = range

    def set_NO_of_discetized_P(self, n):
        self.nDiscrt = n
        self.PInterval = (self.PUpperBound - self.PLowerBound) / (self.nDiscrt - 1)
        self.initialization()

    # 初始化
    def initialization(self):

        # 初始化状态量和控制量空间
        self.Fmass = [[[0 for m in range(self.mDiscrt)] for i in range(self.nDiscrt)]for j in range(self.k)]
        self.P_req = [[[0 for m in range(self.mDiscrt)] for i in range(self.nDiscrt)]for j in range(self.k)]
        self.costF = [[[-1 for m in range(self.mDiscrt)] for i in range(self.nDiscrt)]for j in range(self.k)]
        self.SoC = [[self.SoCLowerBound + i*self.SoCInterval for i in range(self.mDiscrt)]for j in range(self.k)]
        self.PEngine = [[self.PLowerBound + i*self.PInterval for i in range(self.nDiscrt)]for j in range(self.k)]
        # self.costF[self.k - 1] = [[0 for m in range(self.mDiscrt)] for n in range(self.nDiscrt)]

        # 初始化路径空间,防空
        self.Proute = [[[[-1,-1] for m in range(self.mDiscrt)] for n in range(self.nDiscrt)] for k in range(self.k)]

        print("data space initialized")
        # 为变化的末态P预留的空间
        # self.
    # 设定初态SoC

    def set_initial_SoC(self, init_SoC):
        self.init_SoC =init_SoC

    def set_finaL_values_of_SoC(self, final_SoC):
        final_SoC_index = int((final_SoC - self.SoCLowerBound)/self.SoCInterval)
        for i in range(self.nDiscrt):
            self.costF[self.k - 1][i][final_SoC_index] = 0


    def DP_PandSoC_as_state_var(self):
        # 逆向计算
        for k in range(self.k-1,0,-1):
            self.step_to_step_calculator_P_and_SoC_state_var(k)
        # 遍历寻找初态最低的Fmass
        outer = pd.DataFrame(data=self.costF)
        outer.to_csv("cF.csv")
        minFC_index = [-1, -1]  # 防空
        minFC = 100  # 初始
        init_SoC_index = int(self.init_SoC/self.SoCInterval - 0.5)
        init_SoC_search_range = [init_SoC_index-5, init_SoC_index+5]
        if init_SoC_search_range[0]<0:
            temp = 0 - init_SoC_search_range[0]
            init_SoC_search_range[0] = 0
            init_SoC_search_range[1] = init_SoC_search_range[1] + temp
        elif init_SoC_search_range[1]>self.mDiscrt:
            temp = init_SoC_search_range[1] - self.mDiscrt
            init_SoC_search_range[1] = self.mDiscrt
            init_SoC_search_range[0] = init_SoC_search_range[0] - temp

        for m in range(init_SoC_search_range[0], init_SoC_search_range[1]):
            for n in range(self.nDiscrt):
                if 0<self.Fmass[0][n][m]<minFC:
                    minFC_index = [n, m]
                    minFC = self.Fmass[0][n][m]

        # 回溯正确控制
        cursor = list(minFC_index)
        self.finalPe = [0 for i in range(self.k)]
        self.finalSoC = [0 for i in range(self.k)]
        self.finalPreq = [0 for i in range(self.k)]
        self.finalFM = [0 for i in range(self.k)]
        for index in range(self.k):
            print(index)
            self.finalPe[index] = self.PEngine[index][cursor[0]]
            self.finalSoC[index] = self.SoC[index][cursor[1]]
            # 计算需求功率[不算了]
            # state = [self.Fmass[index][cursor[0]][cursor[1]],
            #          self.PEngine[index][cursor[0]],
            #          self.SoC[index][cursor[1]],
            #          self.costF[index][cursor[0]][cursor[1]]]
            # profile = self.profile[index]
            #
            self.finalPreq[index] = self.P_req[index][cursor[0]][cursor[1]]
            self.finalFM[index] = self.Fmass[index][cursor[0]][cursor[1]]
            cursor = self.Proute[index][cursor[0]][cursor[1]]
        return [minFC_index, minFC], [self.finalPe, self.finalPreq, self.finalFM, self.finalSoC]


    # def DP_P_SoC_as_state_var(self):
    #     # 逆向计算
    #     for k in range(self.k):
    #         self

    def step_to_step_calculator_P_and_SoC_state_var(self, k): #k的定义：时间点对应的列表索引 而非逻辑索引
        #读取当前风速等信息
        if k == 0:
            print("out of boundary")
        # elif k == 1:
        #     # K的边界检查在本方法的外部进行
        #     wspeed = self.profile[k - 1][6]
        #     self.case.set_wind(wspeed)
        #     # 读入上一个时间步的飞行条件，profile[t h u v flightmode hfmode wspeed]
        #     hfMode = self.profile[k-1][5]
        #     flightMode = self.profile[k-1][4]
        #     u_expect = self.profile[k-1][2]
        #     v_expect = self.profile[k-1][3]
        #     # h 好像是多余的
        #     # 传递给模型
        #     self.case.HFlightMode = hfMode
        #     self.case.flight_stat = flightMode
        #     self.case.set_u_ideal(u_expect)
        #     self.case.set_vertical_speed(v_expect)
        #     # 计算
        #     self.init_state_sticker(k)
        else:
            # K的边界检查在本方法的外部进行
            wspeed = self.profile[k - 1][7]
            # print("wspeed is in outer iter " + str(wspeed))
            self.case.set_wind(wspeed)
            # 读入上一个时间步的飞行条件
            hfMode = self.profile[k-1][6]
            flightMode = self.profile[k-1][5]
            u_expect = self.profile[k - 1][4]
            v_expect = self.profile[k - 1][3]
            h = self.profile[k - 1][2]
            # 传递变量
            self.case.set_HF_mode(hfMode)
            self.case.set_flight_mode(flightMode)
            self.case.set_u_ideal(u_expect)
            self.case.set_vertical_speed(v_expect)
            self.case.set_height(h)
            # 计算
            if k == self.k - 1:
                cFn = self.costF[k]
                outer = pd.DataFrame(data=cFn)
                outer.to_csv("cFn.csv")
            self.StateUpdater_P_and_SoC_state_var(k)
            # print(self.SoC[k])
            # print(self.costF[k-1])

    def StateUpdater_P_and_SoC_state_var(self,k):
        # 计算两个状态间的油量、SoC变化在ControlEffMod里进行,n是功率点的索引序号,k是当前的时间步数
        # 后向计算
        # 从状态空间中的每个状态点依次向前更新,状态空间是二维的
        # print(self.Fmass[k][1])
        print("theta is "+ str(self.case.theta))
        max_SoC_swap = 0
        SoC_k = 0
        for PStateIndex in range(self.nDiscrt):
            for SoCStateIndex in range(self.mDiscrt):
                # 在二维情况下也只需要检查一个cF
                if self.costF[k][PStateIndex][SoCStateIndex] != -1: #检查当前时间点状态点有效性
                    if(k == self.k-1):
                        print('initial activated SoC is '+ str(self.SoC[k][SoCStateIndex]))
                    # print("in")
                    # 确定搜索域 边界：（1）不超过发动机输出边界 （2）不使Pbat超过电池功率边界 （3）SoC不低于0（可以大于1，矫正即可） 由于总需求功率在状态量循环层未知，（2）（3）在计算层检查

                    CurrentStat = [self.Fmass[k][PStateIndex][SoCStateIndex], self.PEngine[k][PStateIndex], self.SoC[k][SoCStateIndex],
                                  self.costF[k][PStateIndex][SoCStateIndex]]
                    # print(CurrentStat)
                    # 确认控制量的搜索域
                    Preq_est = self.temp_case.get_rough_Preq_sectional(CurrentStat, profile[k-1])

                    # 定义安全裕量0.3
                    PbSearchWindow = 1.3
                    UpperBoundIndex = (Preq_est + self.PbMax*PbSearchWindow - self.PLowerBound)/self.PInterval
                    if UpperBoundIndex > self.nDiscrt - 1:
                        UpperBoundIndex = self.nDiscrt - 1
                    else:
                        UpperBoundIndex = int(UpperBoundIndex)

                    if Preq_est - self.PbMax*PbSearchWindow - self.PLowerBound > 0 :
                        LowerBoundIndex = int((Preq_est - self.PbMax*PbSearchWindow - self.PLowerBound)/self.PInterval)
                    else:
                        LowerBoundIndex = 0

                    # 搜索
                    for PengineIndex in range(LowerBoundIndex, UpperBoundIndex):
                        prePengine = self.PEngine[k - 1][PengineIndex]
                        # 生成Stat，格式[Fmass, Pengine, SoC, costF]

                        # 迭代计算前向
                        # print('Peindex is '+str(PengineIndex))
                        # print('Cstat is' +str(CurrentStat) )

                        tempStat = list(CurrentStat)

                        backwardStat, Preq,w_check,rFC_CHECK = self.case.sectional_compt(tempStat, prePengine)

                        # debug 用


                        if backwardStat[0]<0 and backwardStat[0] != -1:
                            print('error')
                            print(self.case.T)
                            print('time sequo is' + str(k))
                            print('stat space coord is ' + str([PStateIndex, SoCStateIndex]))
                            print(self.case.ESC.get_ESC_power())
                            error = 1
                        # 更新前向点, 该方法仅与输入点的值有关，与状态空间的选定无关
                        # 但需要确定一下结果检测是不是和双状态兼容

                        if backwardStat[3] != -1: #检查本次计算结果有没有意义
                            # print('changed')
                            # 需要吸附到有效点,
                            # if PengineIndex == 48:
                            #     print("FC check case OUTER")
                            #     print("Pen is 13.25, wfuel = " + str(w_check) + "rFC = " + str(rFC_CHECK))
                            priSoCIndex = (backwardStat[2] - self.SoCLowerBound)/self.SoCInterval


                            priSoCIndex = int(priSoCIndex + 0.5) # 四舍五入取整


                            if self.costF[k - 1][PengineIndex][priSoCIndex] == -1:

                                # if PengineIndex%10 == 0:
                                # print('init cF case')

                                if  priSoCIndex==1000 and SoCStateIndex == 1000:
                                    print("selected scenario INIT Preq " + str(Preq))
                                    print("Peng " + str(self.PEngine[k-1][PengineIndex]))
                                    print("delta SOc k - k_-1 " + str(CurrentStat[2] - self.SoC[k-1][priSoCIndex]))
                                    print("delta Mf k-1 - k " + str(backwardStat[0] - CurrentStat[0]))
                                    # 油耗合理性计算
                                self.costF[k - 1][PengineIndex][priSoCIndex] = 0
                                self.Fmass[k - 1][PengineIndex][priSoCIndex] = backwardStat[0]
                                self.P_req[k - 1][PengineIndex][priSoCIndex] = Preq
                                self.Proute[k - 1][PengineIndex][priSoCIndex] = [PStateIndex, SoCStateIndex]
                                # if PengineIndex == 48:
                                #     print("FC check case INIT")
                                #     print("Pen is 13.25, wfuel = "+str(w_check) + "rFC = " + str(rFC_CHECK))
                                #     print("mF change is " + str(self.Fmass[k - 1][PengineIndex][priSoCIndex] - CurrentStat[0]))

                                # if self.SoC[k - 1][priSoCIndex] > max_SoC_swap:
                                #     max_SoC_swap = self.SoC[k - 1][priSoCIndex]
                                #     SoC_k = self.SoC[k][SoCStateIndex]
                                # debug 输出
                                # if PengineIndex >135:
                                #     # print("backword STATIS " + str(backwardStat))
                                #     # print("over charge priSoC is " + str(self.SoC[k - 1][priSoCIndex]) +
                                #     #       "curretn SoC is " + str(self.SoC[k][SoCStateIndex]) + "P_bat is" + str(
                                #     #     self.case.ESC.get_ESC_power() / 1000 - self.PEngine[k][PengineIndex]))
                                #     print("limit Pen" + str(self.PEngine[k-1][PengineIndex]))
                                #     print("wfuel" + str(self.Fmass[k - 1][PengineIndex][priSoCIndex] - self.Fmass[k][PStateIndex][SoCStateIndex]))
                            else:
                                # 优化目标是油量
                                if backwardStat[0] < self.Fmass[k - 1][PengineIndex][priSoCIndex]:
                                # 替换
                                #     if PengineIndex % 10 == 0:
                                #         print('swap case')

                                    if priSoCIndex==1000 and SoCStateIndex == 1000:
                                        print("selected scenario SWAP Preq " + str(Preq))
                                        print("Peng " + str(self.PEngine[k-1][PengineIndex]))
                                        print("delta SOc k - k_-1 " + str(CurrentStat[2] - self.SoC[k-1][priSoCIndex]))
                                        print("delta Mf k-1 - k " + str(backwardStat[0] - CurrentStat[0]))

                                    self.Fmass[k - 1][PengineIndex][priSoCIndex] = backwardStat[0]
                                    self.P_req[k - 1][PengineIndex][priSoCIndex] = Preq
                                    self.Proute[k - 1][PengineIndex][priSoCIndex] = [PStateIndex, SoCStateIndex]
                                    # if PengineIndex == 48:
                                    #     print("FC check case SWAP")
                                    #     print("Pen is 13.25, wfuel = " + str(w_check) + "rFC = " + str(rFC_CHECK))
                                    #     print("mF change is " + str(
                                    #         self.Fmass[k - 1][PengineIndex][priSoCIndex] - CurrentStat[0]))
                                    if self.SoC[k-1][priSoCIndex]>max_SoC_swap:
                                        max_SoC_swap = self.SoC[k-1][priSoCIndex]
                                        SoC_k = self.SoC[k][SoCStateIndex]
                                    # debug 输出
                                    # if PengineIndex>135:
                                    #     print("limit Pen" + str(self.PEngine[k - 1][PengineIndex]))
                                    #     print("wfuel" + str(
                                    #         self.Fmass[k - 1][PengineIndex][priSoCIndex] - self.Fmass[k][PStateIndex][
                                    #         SoCStateIndex]))


                                # print('swap case NEW CF IS ' + str(self.costF[k - 1][PengineIndex]))
                                # print(self.costF[k - 1])
            # print('PE ITER '+ str(PStateIndex) + ' finished')
        self.SoC_max_increase_sequence.append([max_SoC_swap,SoC_k])
        ctrlPrt = pd.DataFrame(data=self.Proute[k-1])
        name = "prtrecord\Prt" + str(k-1) + ".csv"
        ctrlPrt.to_csv(name)
        print("finished step: "+str(k)+" current Fmass is ")
        # print(self.SoC[k - 1])
        # --print(self.Fmass[k-1])

    def export_slices(self):
        mF0 = self.Fmass[0]
        outer = pd.DataFrame(data=mF0)
        outer.to_csv("mF0.csv")
        SoC0 = self.SoC[0]
        outer = pd.DataFrame(data=SoC0)
        outer.to_csv("SoC0.csv")
        if self.k>30:
            mF30 = self.Fmass[30]
            outer = pd.DataFrame(data=mF30)
            outer.to_csv("mF30.csv")
            SoC30 = self.SoC[30]
            outer = pd.DataFrame(data=SoC30)
            outer.to_csv("SoC30.csv")
        if self.k > 50:
            mF50 = self.Fmass[50]
            outer = pd.DataFrame(data=mF50)
            outer.to_csv("mF50.csv")
            SoC50 = self.SoC[50]
            outer = pd.DataFrame(data=SoC50)
            outer.to_csv("SoC50.csv")
        if self.k > 70:
            mF70 = self.Fmass[70]
            outer = pd.DataFrame(data=mF70)
            outer.to_csv("mF70.csv")
            SoC70 = self.SoC[70]
            outer = pd.DataFrame(data=SoC70)
            outer.to_csv("SoC70.csv")
        if self.k > 90:
            mF90 = self.Fmass[90]
            outer = pd.DataFrame(data=mF90)
            outer.to_csv("mF90.csv")
            SoC90 = self.SoC[90]
            outer = pd.DataFrame(data=SoC90)
            outer.to_csv("SoC90.csv")





    # def init_state_sticker(self,k):
    #     if k!=1:
    #         print("wrong call")
    #     else:
    #         for StateIndex in range(self.nDiscrt):
    #             if self.costF[k][StateIndex] != -1:
    #
    #                 for PengineIndex in range(self.nDiscrt):
    #                     prePengine = self.PEngine[k - 1][PengineIndex]
    #                     fowardStat = [self.Fmass[k][StateIndex], self.PEngine[k][StateIndex],
    #                                   self.SoC[k][StateIndex], self.costF[k][StateIndex]]
    #                     backwardStat = self.case.sectional_compt(fowardStat, prePengine, self.profile[k - 1], k)# 暂时没有迭代 迭代的话也写在这里面
    #                     if backwardStat[3] != -1 and  backwardStat[2] > 0:
    #                         self.Fmass[k - 1][PengineIndex] = backwardStat[0]
    #                         self.SoC[k - 1][PengineIndex] = backwardStat[2]
    #                         self.costF[k - 1][PengineIndex] = backwardStat[3]



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
dry_weight = 40+13#干重，包括载荷但不包括电池 [kg]
max_fuel_mass = 12#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 300#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]

theta = 5
t = [0]
max_P = 0

flight = Flight(S,dry_weight,max_fuel_mass,capacity,dt = dt)
flight.set_plane()
print('--rotyor number is' + str(flight.case.n))

profile = profile_reader()
# print(profile)
test = DP_calculator_withSoC(profile,flight.case)
# test.set_NO_of_discetized_P(141)
# test.set_initial_values_of_SoC(0.3)
test.set_finaL_values_of_SoC(0.3)
result,optCtrl = test.DP_PandSoC_as_state_var()
print(result)
test.export_slices()
plt.figure(4)
#plt.plot( Hf_t, miu_motor)
plt.subplot(2,1,1)
t = [i*5 for i in range(test.k-1)]

plt.plot(t, optCtrl[0][:-1], label = 'PGE')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t, optCtrl[1][:-1],"red", label = 'preq')
plt.ylabel(r"P /kW")
plt.legend(loc=0,ncol=1,fontsize=14)
plt.subplot(2,1,2)
plt.plot(t, optCtrl[3][:-1], label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('time /s')

plt.show()
outer = pd.DataFrame(data=optCtrl)
outer.to_csv("optDP.csv")

SoCINcre = pd.DataFrame(data = test.SoC_max_increase_sequence)
SoCINcre.to_csv("SOcINCRE.csv")
# print(a)
#version ontol




