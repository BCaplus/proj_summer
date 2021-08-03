# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from ControlEfficiencyModel import static_model

S = 4 # 最大截面面积 [m^2]
cd1 = 0.5 #平飞阻力系数 来自于文献
cd2 = 1.5 #90度俯仰角阻力系数
dry_weight = 40+25#干重，包括载荷但不包括电池 [kg]
max_fuel_mass = 12#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 900#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]
Height = 200 #定高飞行
Height_2nd = 700
theta = 5
t = [0]
max_P = 0
T = np.loadtxt("Tdata.csv",dtype=float, delimiter=",",skiprows=0)

case = static_model(S, cd1, cd2, dry_weight, max_fuel_mass, dt, capacity, Ub)
case_rule = static_model(S, cd1, cd2, dry_weight, max_fuel_mass, dt, capacity, Ub)
# case.powerSys.ecms.Bat.SoCH = 540/capacity
# case.powerSys.ecms.Bat.SoCL = 270/capacity
print('model set')

counter = 0

while case.h < Height:
    # ecms
    t_index = int(case.t/dt)
    case.set_T(T[t_index][1])
    case.set_vertical_speed(1)
    case.FlightStat = 0
    case.update_ECMS(wind=2)
    # rule
    case_rule.set_wind(case.get_wind_speed())
    case_rule.set_vertical_speed(1)
    case_rule.FlightStat = 0
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()
    counter += 1

climb_fuel_consumed = max_fuel_mass - case.powerSys.get_fuelmass()
fuel_left = case.powerSys.get_fuelmass()

print("phase1 done P = "+str(case.h))

HFstat = [[0,0,0,0]] #u, p_ge, miu_ESC, miu_Motor
Hf_t = [0]
while case.powerSys.get_fuelmass()>0.5*max_fuel_mass:
    case.FlightStat = 1
    case.HFlightMode = 0
    case.set_ideal_theta(theta)
    t_index = int(case.t/dt)
    case.set_T(T[t_index][1])


    # ECMS
    case.update_ECMS(wind=2)
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

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()

    counter += 1
print("phase2 done h = "+str(case.h))
phase1done = counter

while case.h< Height_2nd:
    t_index = int(case.t/dt)
    case.set_T(T[t_index][1])
    case.set_vertical_speed(0.2)
    case.FlightStat = 0
    case.update_ECMS(wind=2)

    case_rule.set_vertical_speed(0.2)
    case_rule.FlightStat = 0
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power() > max_P:
        max_P = case.powerSys.get_ge_power()

    counter += 1
print("phase3 done h = "+str(case.h))

while case.powerSys.get_fuelmass()>1.5:

    # ecms
    t_index = int(case.t/dt)
    case.set_T(T[t_index][1])
    case.FlightStat = 1
    #case.HFlightMode = 1
    #case.set_u_ideal(12)
    case.HFlightMode = 0
    case.set_ideal_theta(theta)

    case.update_ECMS(wind=2)

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
while case.h>0:

    t_index = int(case.t/dt)
    case.set_vertical_speed(-0.5)
    case.FlightStat = 2
    if t_index < len(T):
        case.set_T(T[t_index][1])
        case.update_ECMS(wind=2)
    else:
        case.update_ECMS(wind=1)

    case_rule.set_vertical_speed(-0.5)
    case_rule.FlightStat = 2
    case_rule.update(wind=1, mode = 1, T_out= case.T)

    t.append(case.t)

    if case.powerSys.get_ge_power()>max_P:
        max_P = case.powerSys.get_ge_power()
    counter += 1


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




plt.figure(1)
#plt.plot( Hf_t, miu_motor)
plt.subplot(2,1,1)
plt.plot(t, P_GE, label = 'Generator Power Output')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t, P_need,"yellow", label = 'Motor Power Demand')
plt.ylabel(r"power(W)")
plt.ylim(0,16000)
plt.xlim(0,case.t+500)
plt.legend(loc=0,ncol=1)
plt.subplot(2,1,2)
plt.plot(t, SoC, label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('time(s)')
plt.ylim(0,1)
plt.xlim(0,case.t+500)
plt.show()

plt.figure(2)
#plt.plot( Hf_t, miu_motor)
plt.subplot(2,1,1)
plt.plot(t, P_GE_rule, label = 'Generator Power Output')
#plt.plot(t, average_P_GE, "r--", label = 'Averaged GE Power')
plt.plot(t, P_need_rule,"yellow", label = 'Motor Power Demand')
plt.ylabel(r"power(W)")
plt.ylim(0,16000)
plt.xlim(0,case.t+500)
plt.legend(loc=0,ncol=1)
plt.subplot(2,1,2)
plt.plot(t, SoC_rule, label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('time(s)')
plt.ylim(0,1)
plt.xlim(0,case.t+500)


plt.rcParams['font.sans-serif']=['FangSong']
plt.figure(3)
plt.plot(t[0:phase1done], P_need[0:phase1done],"yellow", label = '第一阶段')
plt.title("阶段(A)功率需求")
plt.figure(4)
plt.plot(t[phase1done+1:counter], P_need_rule[phase1done+1:counter],"yellow", label = '第二阶段')
plt.title("阶段(B)功率需求")
plt.show()

# T = np.array(T)
# print(T)
# np.savetxt('Tdata.csv', T, delimiter = ',')