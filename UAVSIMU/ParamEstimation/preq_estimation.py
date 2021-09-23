from ControlEfficiencyModel import static_model
from case_generator import Flight
import os
import pandas as pd

def profile_reader():
    path = os.getcwd() + '\profile.csv'
    print('step1 done')
    profile = pd.read_csv(path)
    print('step2 done')
    profile = profile.values.tolist()
    print('step3 done')
    return profile


S = 4 # ��������� [m^2]
cd1 = 0.5 #ƽ������ϵ�� ����������
cd2 = 1.5 #90�ȸ���������ϵ��
dry_weight = 40+23#���أ������غɵ���������� [kg]
max_fuel_mass = 12#���Я��ȼ������ [kg]
dt = 5  #ʱ�䲽�� [s]
capacity = 900#������� [Wh] ��Ҫ���������ڵĽű���Ĳ�������һ��
Ub = 60 #������·��ѹ [V]
Height = 200 #���߷���
Height_2nd = 700
theta = 5
t = [0]
max_P = 0

flight = Flight(S,dry_weight,max_fuel_mass,capacity,dt = dt)
flight.set_plane()
print('--rotyor number is' + str(flight.case.n))
profile = profile_reader()

for k in range(len(profile)):


