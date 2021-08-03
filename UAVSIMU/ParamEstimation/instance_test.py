# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import csv
import pandas as pd
from ControlEfficiencyModel import static_model

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

T=[]

P_demand = []
F_consump_ecms = []
F_consump_rule = []
F_consump_r_ecms = []
F_consump_r_rule = []

eff = []
case = static_model(S, cd1, cd2, dry_weight, max_fuel_mass, dt, capacity, Ub)
case_rule = static_model(S, cd1, cd2, dry_weight, max_fuel_mass, dt, capacity, Ub)
# case.powerSys.ecms.Bat.SoCH = 540/capacity
# case.powerSys.ecms.Bat.SoCL = 270/capacity
print('model set')

counter = 0

while case.h < Height:
    # ecms
    case.set_vertical_speed(1)
    case.FlightStat = 0
    case.update_ECMS(wind=1)
    # rule
    case_rule.set_wind(case.get_wind_speed())
    case_rule.set_vertical_speed(1)
    case_rule.FlightStat = 0
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()
    counter += 1
    P_demand.append([case.t, case.T])

    # 油耗监视
    F_consump_ecms.append(case.get_fuel_C())
    F_consump_rule.append(case_rule.get_fuel_C())
    F_consump_r_ecms.append(case.get_fuel_reduced_C())
    F_consump_r_rule.append(case_rule.get_fuel_reduced_C())
    eff.append(case.get_eff_elec())

climb_fuel_consumed = max_fuel_mass - case.powerSys.get_fuelmass()
fuel_left = case.powerSys.get_fuelmass()

print("phase1 done P = "+str(case.h))

HFstat = [[0,0,0,0]] #u, p_ge, miu_ESC, miu_Motor
Hf_t = [0]
while case.powerSys.get_fuelmass()>0.5*max_fuel_mass:
    case.FlightStat = 1
    case.HFlightMode = 0
    case.set_ideal_theta(theta)

    # ECMS
    case.update_ECMS(wind=1)
    # RULE
    case_rule.FlightStat = 1
    case_rule.HFlightMode = 0
    case_rule.set_ideal_theta(theta)
    case_rule.set_wind(case.get_wind_speed())
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    #print(case.powerSys.get_ge_power())
    HFstat.append([case.u, case.powerSys.get_ge_power(), case.get_ESC_efficiency(), case.get_Motor_efficiency()])

    t.append(case.t)

    Hf_t.append(case.t)
    F_consump_ecms.append(case.get_fuel_C())
    F_consump_rule.append(case_rule.get_fuel_C())
    F_consump_r_ecms.append(case.get_fuel_reduced_C())
    F_consump_r_rule.append(case_rule.get_fuel_reduced_C())

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()

    T.append([case.t, case.T])
    eff.append(case.get_eff_elec())
    counter += 1
print("phase2 done h = "+str(case.h))
phase1done = counter

while case.h< Height_2nd:
    case.set_vertical_speed(0.2)
    case.FlightStat = 0
    case.update_ECMS(wind=1)

    case_rule.set_vertical_speed(0.2)
    case_rule.FlightStat = 0
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power() > max_P:
        max_P = case.powerSys.get_ge_power()

    T.append([case.t, case.T])
    F_consump_ecms.append(case.get_fuel_C())
    F_consump_rule.append(case_rule.get_fuel_C())
    F_consump_r_ecms.append(case.get_fuel_reduced_C())
    F_consump_r_rule.append(case_rule.get_fuel_reduced_C())
    counter += 1
    eff.append(case.get_eff_elec())

print("phase3 done h = "+str(case.h))

while case.powerSys.get_fuelmass()>1.5:

    # ecms
    case.FlightStat = 1
    #case.HFlightMode = 1
    #case.set_u_ideal(12)
    case.HFlightMode = 0
    case.set_ideal_theta(theta)

    case.update_ECMS(wind=1)

    # rule
    case_rule.FlightStat = 1
    # case.HFlightMode = 1
    # case.set_u_ideal(12)
    case_rule.HFlightMode = 0
    case_rule.set_ideal_theta(theta)

    case_rule.update(wind=1, mode = 1, T_out= case.T)

    #print(case.powerSys.get_ge_power())
    HFstat.append([case.u, case.powerSys.get_ge_power(), case.get_ESC_efficiency(), case.get_Motor_efficiency()])

    Hf_t.append(case.t)
    t.append(case.t)

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()
    counter += 1
    F_consump_ecms.append(case.get_fuel_C())
    F_consump_rule.append(case_rule.get_fuel_C())
    F_consump_r_ecms.append(case.get_fuel_reduced_C())
    F_consump_r_rule.append(case_rule.get_fuel_reduced_C())
    T.append([case.t, case.T])
    eff.append(case.get_eff_elec())

while case.h>0:
    case.set_vertical_speed(-0.5)
    case.FlightStat = 2
    case.update_ECMS(wind=1)

    case_rule.set_vertical_speed(-0.5)
    case_rule.FlightStat = 2
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()
    T.append([case.t, case.T])
    F_consump_ecms.append(case.get_fuel_C())
    F_consump_rule.append(case_rule.get_fuel_C())
    F_consump_r_ecms.append(case.get_fuel_reduced_C())
    F_consump_r_rule.append(case_rule.get_fuel_reduced_C())
    counter += 1
    eff.append(case.get_eff_elec())


print("height = "+str(case.h))
print("rule height = "+str(case_rule.h))
print("t = " + str(case.t) + "\n")
HF_fuel_consumed = fuel_left - case.powerSys.get_fuelmass()
ratioClimb = climb_fuel_consumed/max_fuel_mass
ratioHF = HF_fuel_consumed/max_fuel_mass
print("climb rate = " + str(ratioClimb) + "\n")
print("HF rate = " + str(ratioHF) + "\n")
print("ruel f left = " + str(case_rule.powerSys.get_fuelmass()) + "\n")
print("fuel left = " + str(case.powerSys.get_fuelmass()) + "\n")
print("maxGe = " + str(max_P))


flight_stat = case.get_flight_stat()
Bat_stat = case.get_Bat_stat()

u = [item[0] for item in flight_stat]
u_HF = [item[0] for item in HFstat]
P_HF = [item[1] for item in HFstat]
miu_ESC = [item[2] for item in HFstat]
miu_motor = [item[3] for item in HFstat]
average_P = sum(P_HF)/len(P_HF)
average_u = sum(u_HF)/len(u_HF)
L = [item[3] for item in flight_stat]
SoC = [item[5] for item in flight_stat]
P_need = [item[6] for item in flight_stat]
P_GE = [item[7] for item in flight_stat]
#average_P_GE = signal.savgol_filter(P_GE,501,4)

Bat_heat = [item[0] for item in Bat_stat]

ave_Bat_heat = sum(Bat_heat)/len(Bat_heat)
Bat_I = [abs(item[1]) for item in Bat_stat]
ave_Bat_i = sum(Bat_I)/len(Bat_I)

flight_stat_rule = case_rule.get_flight_stat()
Bat_stat_rule = case_rule.get_Bat_stat()
P_need_rule = [item[6] for item in flight_stat_rule]
P_GE_rule = [item[7] for item in flight_stat_rule]
SoC_rule = [item[5] for item in flight_stat_rule]


Bat_heat_rule = [item[0] for item in Bat_stat_rule]
ave_Bat_heat_rule = sum(Bat_heat_rule)/len(Bat_heat_rule)
Bat_I_rule = [abs(item[1]) for item in Bat_stat_rule]
ave_Bat_i_rule = sum(Bat_I_rule)/len(Bat_I_rule)


print("average u = " + str(average_u) + "\n")
print("average P = " + str(average_P) + "\n")
print("L = " + str(L[len(L) - 1]) + "\n")
print("t = " + str(t[len(t) - 1]) + "\n")
print("ave heat =" + str(ave_Bat_heat) )
print("ave bat I =" + str(ave_Bat_i) )

print("ave heat rule=" + str(ave_Bat_heat_rule) )
print("ave bat I rule =" + str(ave_Bat_i_rule) )

print("case T " + str(case.t))
print("points no " + str(len(P_GE)*case.dt))

# 保存拉力数据

plt.rcParams['savefig.dpi'] = 300

plt.rcParams['figure.dpi'] = 300

config = {
    "font.family":'serif',
    "font.size": 16,
    "mathtext.fontset":'stix',
    "font.serif": ['SimSun'],
}
plt.rcParams.update(config)
plt.figure(1)
#plt.plot( Hf_t, miu_motor)
plt.subplot(2,1,1)
plt.plot(t, P_GE, label = '发动机输出功率')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t, P_need,"red", label = '功率需求')
plt.ylabel(r"功率 /W")
plt.ylim(0,16000)
plt.xlim(0,case.t+500)
plt.legend(loc=0,ncol=1,fontsize=14)
plt.subplot(2,1,2)
plt.plot(t, SoC, label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('时间 /s')
plt.ylim(0,1)
plt.xlim(0,case.t+500)
plt.show()

plt.figure(2)
#plt.plot( Hf_t, miu_motor)
plt.subplot(2,1,1)
plt.plot(t, P_GE_rule, label = '发动机输出功率')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t, P_need_rule,"yellow", label = '功率需求')
plt.ylabel(r"功率 /W")
plt.ylim(0,16000)
plt.xlim(0,case.t+500)
plt.legend(loc=0,ncol=1,fontsize=14)
plt.subplot(2,1,2)
plt.plot(t, SoC_rule, label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('时间 /s')
plt.ylim(0,1)
plt.xlim(0,case.t+500)



plt.figure(3)
plt.plot(t[0:phase1done], P_need[0:phase1done],"red", label = '第一阶段')
plt.title("阶段(A)",y=-0.3,fontsize=14)
plt.ylabel('功率 /W')
plt.xlabel('时间 /s')
plt.figure(4)
plt.plot(t[phase1done+1:counter], P_need_rule[phase1done+1:counter],"red", label = '第二阶段')
plt.title("阶段(B)",y=-0.3,fontsize=14)
plt.ylabel('功率 /W')
plt.xlabel('时间 /s')


# T = np.array(T)
# print(T)
# np.savetxt('Tdata.csv', T, delimiter = ',')

plt.figure(5)
# f5.set_title("阶段(A)",y=-0.3,fontsize=14)
plt.subplot(2,1,1)

plt.plot(t[0:phase1done], P_GE_rule[0:phase1done], "blue",label = '规则控制下发动机输出功率')
plt.plot(t[0:phase1done], P_GE[0:phase1done], "green",label = 'ECMS优化下发动机输出功率')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t[0:phase1done], P_need[0:phase1done],"red", label = '功率需求')
plt.ylabel(r"功率 /W")
plt.ylim(0,16000)
plt.yticks([0,10000,12500,15000],size=12)
plt.xlim(0,dt*phase1done+500)
plt.legend(loc=0,ncol=1,fontsize=12)
plt.subplot(2,1,2)
plt.plot(t[0:phase1done], SoC_rule[0:phase1done],"blue", label = '规则控制下SoC')
plt.plot(t[0:phase1done], SoC[0:phase1done],"green", label = 'ECMS下SoC')
plt.ylabel('SoC')
plt.xlabel('时间 /s')
# plt.title("阶段(A)",y=-0.65,fontsize=14)
plt.ylim(0,1)

plt.xlim(0,dt*phase1done+500)

plt.figure(6)
# plt.title("阶段(B)",y=-0.3,fontsize=14)
plt.subplot(2,1,1)

plt.plot(t[phase1done+1:counter], P_GE_rule[phase1done+1:counter], "blue",label = '规则控制下发动机输出功率')
plt.plot(t[phase1done+1:counter], P_GE[phase1done+1:counter], "green",label = 'ECMS优化下发动机输出功率')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t[phase1done+1:counter], P_need[phase1done+1:counter],"red", label = '功率需求')
plt.ylabel(r"功率 /W")
plt.ylim(0,16000)
plt.yticks([0,10000,12500,15000],size=12)
plt.xlim(phase1done*dt,counter*dt+500)
plt.legend(loc=0,ncol=1,fontsize=12)
plt.subplot(2,1,2)
plt.plot(t[phase1done+1:counter], SoC_rule[phase1done+1:counter], "blue", label = '规则控制下SoC')
plt.plot(t[phase1done+1:counter], SoC[phase1done+1:counter], "green",label = 'ECMS下SoC')
plt.ylabel('SoC')
plt.xlabel('时间 /s')
plt.ylim(0,1)
# plt.title("阶段(B)",y=-0.65,fontsize=14)
plt.xlim(phase1done*dt,counter*dt+500)

plt.figure(7)
FCE_AVE = signal.savgol_filter(F_consump_ecms,501,4)
FCE_AVE_R = signal.savgol_filter(F_consump_rule,501,4)
plt.title("阶段(A)",y=-0.3,fontsize=14)
plt.plot(t[0:phase1done], F_consump_ecms[0:phase1done],"blue", label = 'ECMS下燃油消耗率')
plt.plot(t[0:phase1done], F_consump_rule[0:phase1done],"orange", label = '规则控制下燃油消耗率')
plt.plot(t[0:phase1done], FCE_AVE[0:phase1done],"blue",linestyle=":", label = 'ECMS油耗平均值')
plt.plot(t[0:phase1done], FCE_AVE_R[0:phase1done],"orange",linestyle=":", label = '规则控制下油耗平均值')
plt.ylabel('耗油量 /(kg/s)')
plt.xlabel('时间 /s')
plt.legend(loc=0,ncol=1,fontsize=14)
plt.xlim(0,dt*phase1done+500)

plt.figure(8)
plt.title("阶段(B)",y=-0.3,fontsize=14)
plt.plot(t[phase1done+1:counter], F_consump_ecms[phase1done+1:counter], label = 'ECMS下燃油消耗率')
plt.plot(t[phase1done+1:counter], F_consump_rule[phase1done+1:counter], label = '规则控制下燃油消耗率')
plt.plot(t[phase1done+1:counter], FCE_AVE[phase1done+1:counter],"blue",linestyle=":", label = 'ECMS油耗平均值')
plt.plot(t[phase1done+1:counter], FCE_AVE_R[phase1done+1:counter],"orange",linestyle=":", label = '规则控制下油耗平均值')
plt.ylabel('耗油量 /(kg/s)')
plt.xlabel('时间 /s')
plt.legend(loc=0,ncol=1,fontsize=14)
plt.xlim(phase1done*dt,counter*dt+500)

plt.figure(9)
plt.title("阶段(A)",y=-0.3,fontsize=14)
plt.plot(t[0:phase1done], F_consump_r_ecms[0:phase1done], label = 'ECMS下比油耗')
plt.plot(t[0:phase1done], F_consump_r_rule[0:phase1done], label = '规则控制下比油耗')
plt.ylabel('耗油量 /(g/kW·h)')
plt.xlabel('时间 /s')
plt.legend(loc=0,ncol=1,fontsize=14)
plt.xlim(0,dt*phase1done+500)

plt.figure(10)
plt.title("阶段(B)",y=-0.3,fontsize=14)
plt.plot(t[phase1done+1:counter], F_consump_r_ecms[phase1done+1:counter], label = 'ECMS下比油耗')
plt.plot(t[phase1done+1:counter], F_consump_r_rule[phase1done+1:counter], label = '规则控制下比油耗')
plt.ylabel('耗油量 /(g/kW·h)')
plt.xlabel('时间 /s')
plt.legend(loc=0,ncol=1,fontsize=14)
plt.xlim(phase1done*dt,counter*dt+500)
plt.show()

plt.figure(11)

Bat_heat_ave = signal.savgol_filter(Bat_heat,501,4)
Bat_heat_ave_rule = signal.savgol_filter(Bat_heat_rule,501,4)
# plt.title("电池功率损耗对比")
plt.plot(t, Bat_heat_ave, label = 'ECMS下电池平均功率损耗')
plt.plot(t, Bat_heat_ave_rule, label = '规则控制下平均功率损耗')
plt.ylabel('电池内阻上的功率 /W')
plt.xlabel('时间 /s')
plt.legend(loc=0,ncol=1,fontsize=14)
plt.xlim(0,counter*dt+500)


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

eff_ave = signal.savgol_filter(eff,31,4)
ax1.plot(t, P_need,"red", label = '功率需求')
ax2.plot(t[1:], eff_ave,label = '电传动效率')
ax1.set_ylabel('需求功率 /W')
ax2.set_ylabel('传动效率')
ax1.set_xlabel('时间 /s')
plt.show()

print("phase 1 C ecms")