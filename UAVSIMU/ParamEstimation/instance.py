# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy import signal
from ControlEfficiencyModel import static_model
import csv
import pandas as pd

S = 1 # 最大截面面积 [m^2]
cd1 = 0.5 #平飞阻力系数 来自于文献
cd2 = 1.5 #90度俯仰角阻力系数
dry_weight = 40+25#干重，包括载荷但不包括电池 [kg]
max_fuel_mass =10#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 900#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]
Height = 200 #定高飞行
theta = 5
t = [0]
print("data set")
case = static_model(S, cd1, cd2, dry_weight, max_fuel_mass, dt, capacity, Ub)
print('model set')
flight_stat = [[0,0,max_fuel_mass,0,0,1,0,0,0,0]] #水平速度，垂直速度，油量，距离，高度. SOC, 飞行所需功率，发电系统输出功率,FC, 比油耗


while case.h < Height:
    case.set_vertical_speed(2)
    case.FlightStat = 0
    case.update()
    flight_stat.append([case.u, case.v, case.powerSys.fuelMass, case.distance, case.h, case.powerSys.SoC, case.ESC.get_ESC_power(), case.powerSys.get_ge_power(),case.get_fuel_C(),case.get_fuel_reduced_C()])
    t.append(case.t)

climb_fuel_consumed = max_fuel_mass - case.powerSys.get_fuelmass()
fuel_left = case.powerSys.get_fuelmass()

print("phase1 done")
P_demand = case.ESC.get_ESC_power()


HFstat = [[0,0,0,0]] #u, p_ge, miu_ESC, miu_Motor
Hf_t = [0]
while case.powerSys.fuelMass>0.5:
    case.FlightStat = 1
    case.HFlightMode = 1
    case.set_u_ideal(8)
    #case.HFlightMode = 0
    #case.set_ideal_theta(theta)

    case.update()
    #print(case.powerSys.get_ge_power())
    HFstat.append([case.u, case.powerSys.get_ge_power(), case.get_ESC_efficiency(), case.get_Motor_efficiency()])
    flight_stat.append([case.u, case.v, case.powerSys.fuelMass, case.distance, case.h, case.powerSys.SoC, case.ESC.get_ESC_power(), case.powerSys.get_ge_power(),case.get_fuel_C(),case.get_fuel_reduced_C()])
    t.append(case.t)
    Hf_t.append(case.t)
print("phase2 done")
while case.h>0:
    case.set_vertical_speed(-2)
    case.FlightStat = 2
    case.update()
    flight_stat.append(
        [case.u, case.v, case.powerSys.fuelMass, case.distance, case.h, case.powerSys.SoC, case.ESC.get_ESC_power(),
         case.powerSys.get_ge_power(),case.get_fuel_C(),case.get_fuel_reduced_C()])
    t.append(case.t)
print("phase3 done")

HF_fuel_consumed = fuel_left - case.powerSys.get_fuelmass()
ratioClimb = climb_fuel_consumed/max_fuel_mass
ratioHF = HF_fuel_consumed/max_fuel_mass
print("climb rate = " + str(ratioClimb) + "\n")
print("HF rate = " + str(ratioHF) + "\n")

u = [item[0] for item in flight_stat]
v = [item[1] for item in flight_stat]
h = [item[4] for item in flight_stat]
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
FC = [item[8] for item in flight_stat]
sFC = [item[9] for item in flight_stat]
# average_P_GE = signal.savgol_filter(P_GE,501,4)

fly_data = case.get_flight_stat()
bat_data = case.get_Bat_stat()
bat_heat = [bat[0] for bat in bat_data]

colomn = ['power demand','ICE output','soc','FC','specific FC','Battery heat']

data_output = [t,P_need, P_GE, SoC, FC, sFC,bat_heat,u,v,h]
out = pd.DataFrame(data=data_output)
out.to_csv('E:/UAVSIMU/out_csv_interp.csv')

print("average u = " + str(average_u) + "\n")
print("average P = " + str(average_P) + "\n")
print("L = " + str(L[len(L) - 1]) + "\n")
print("t = " + str(t[len(t) - 1]) + "\n")
print("fuel left"+ str(case.powerSys.fuelMass))
print("P demand" + str(P_demand))
#plt.plot( Hf_t, miu_motor)
# plt.subplot(2,1,1)
# plt.plot(t, P_GE, label = 'Generator Power Output')
plt.rcParams['font.sans-serif']=['FangSong']
# plt.plot(t, average_P_GE, "r--", label = '发动机输出功率')
plt.plot(t, P_need,"red", label = 'MTOW = 69 kg')
plt.ylabel(r"功率/ W",fontsize=16)
plt.xlabel(r"爬升顶点高度/ m",fontsize=16)
plt.ylim(8000,12000)
plt.xlim(0,6000)
# plt.title("典型飞行剖面下无人机的功率需求变化")
plt.legend(loc=0,ncol=1)
# plt.subplot(2,1,2)
plt.plot(t, SoC, label = 'SoC')
plt.ylabel('SoC')
plt.xlabel('time(s)')
plt.ylim(0,1)
# plt.xlim(0,10000)
plt.show()