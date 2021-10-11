# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import copy

# 计算用
from ControlEfficiencyModel import static_model
from case_generator import Flight
import pandas as pd
import os

S = 4 # 最大截面面积 [m^2]
cd1 = 0.5 #平飞阻力系数 来自于文献
cd2 = 1.5 #90度俯仰角阻力系数
dry_weight = 40+23#干重，包括载荷但不包括电池 [kg]
max_fuel_mass = 0.5#起飞携带燃油质量 [kg]
dt = 5  #时间步长 [s]
capacity = 900#电池容量 [Wh] 需要与电池类所在的脚本里的参数保持一致
Ub = 60 #动力电路电压 [V]
Height = 200 #定高飞行
Height_2nd = 700
theta = 5
max_P = 0

def profile_reader():
    path = os.getcwd() + '\profile.csv'
    print('step1 done')
    profile = pd.read_csv(path)
    print('step2 done')
    profile = profile.values.tolist()
    print('step3 done')
    return profile

flight = Flight(S,dry_weight,max_fuel_mass,capacity,dt = dt)
flight.set_initial_fuel(2)
flight.set_initial_SoC(0.304)
flight.set_plane()
profile = profile_reader()
flight.load_profile(profile=profile)
print('--rotyor number is' + str(flight.case.n))

flightStat, batStat = flight.simu_ECMS()
flight.plot_flight_stat(flightStat, flight.time_sequence)