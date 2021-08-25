#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import math
import numpy as np
import csv
import xlrd
import matplotlib.pyplot as plt
from xls_columnread import read_bycolumn
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate

filename = ""
_map_shape = [9,13]




class OptimumFC:
    def __init__(self):
        self.c0 = 0  #耗油量拟合曲线零阶系数、
        self.c1 = 0  #一阶系数
        self.map = [[]]
        self.n_upbound = 7500
        self.n_lowerbound = 1000
        self.P_upbound = 15800
        self.P_lowerbound = 1000
        self.min_reduced_FC = 10000 #初始化

    def _take_P(self,ele):
        return ele[0]

    def import_MAP_csv(self, shape = _map_shape):
        temp = np.zeros(shape[0], shape[1])
        with open(filename) as f:
            reader = csv.reader(f)
            row_counter = 0
            for row in reader:
                for i in range(shape[1]):
                    temp[row_counter][i] = row[i]
                row_counter  = row_counter + 1
        self.map = temp
        self.OptimumCalc()

    def import_MAP_xlrd(self, shape = _map_shape):
        # shape[0]是每个同转速组的数据点数，shape[1]是转速级别数
        n = [0 for i in range(shape[1])]
        # m*n*2数组，每单元第一个是功率，第二个是油耗
        group_curve = [[[0.0,0.0] for i in range(shape[0])] for i in range(shape[1])]
        group_curve = np.array(group_curve)
        map = xlrd.open_workbook("Engine map.xls")
        sh = map.sheet_by_name("Sheet2")
        group_counter = 0
        group_header = 2
        lower_P_bound = [20 for i in range(shape[1])]
        upper_P_bound = [0 for i in range(shape[1])]
        while group_counter<shape[1]:
            n[group_counter] = sh.row_values(group_header)[0]

            for row in range(group_header, group_header+shape[0]):

                # if sh.row_values(row)[1] < lower_P_bound[group_counter]:
                #     lower_P_bound[group_counter] = sh.row_values(row)[1]
                if sh.row_values(row)[1] > upper_P_bound[group_counter]:
                    upper_P_bound[group_counter] = sh.row_values(row)[1]
                group_curve[group_counter][row - group_header][0] = sh.row_values(row)[1]
                group_curve[group_counter][row - group_header][1] = sh.row_values(row)[2]
                n[group_counter] = sh.row_values(row)[0]
            group_curve[group_counter] = group_curve[group_counter][group_curve[group_counter][:, 0].argsort()]

            # 过滤掉间距太大的开头一两个点
            cursor = 0
            while cursor<shape[0]-1 and (group_curve[group_counter][cursor+1][0] - group_curve[group_counter][cursor][0]) > 6:
                cursor += 1
            lower_P_bound[group_counter] = group_curve[group_counter][cursor][0]
            plt.scatter(group_curve[group_counter][:, 0], group_curve[group_counter][:, 1])
            group_counter += 1
            group_header += shape[0]


        self.map = group_curve
        self.P_lower_bounds = lower_P_bound

        self.P_upper_bounds = upper_P_bound
        self.P_upbound = max(self.P_upper_bounds)
        self.P_lowerbound = min(self.P_lower_bounds)
        # print(self.P_lowerbound)
        self.OptimumCalc_non_rec()

    def import_map_bycol(self):
        [map, n, upperp, lowerp] = read_bycolumn()
        self.map = map
        self.P_lower_bounds = lowerp
        self.P_upper_bounds = upperp
        self.P_upbound = max(self.P_upper_bounds)
        self.P_lowerbound = min(self.P_lower_bounds)
        self.n_group = n
        self.OptimumCalc_non_rec()

    def MAPFunc(self, n, P, shape = _map_shape):
        while self.n_lowerbound<=n<=self.n_upbound and self.P_lowerbound<=P<=self.P_upbound:
            P_interval = (self.P_upbound - self.P_lowerbound)/shape[0]
            n_interval = (self.n_upbound - self.n_lowerbound)/shape[1]
            P_index = int((P - self.P_lowerbound)/P_interval)
            P_res = (P - self.P_lowerbound)%P_interval
            n_index = int((n - self.n_lowerbound)/n_interval)
            n_res = (n - self.n_lowerbound)%n_interval
            if P_res == 0:
                if n_res == 0:
                    FC = self.map[P_index][n_index]
                else:
                    FC = self.map[P_index][n_index+1]*n_res/n_interval + self.map[P_index][n_index]*(n_interval - n_res)/n_interval
            else:
                if n_res == 0:
                    FC = self.map[P_index+1][n_index] * P_res / P_interval + self.map[P_index][n_index] * (
                                P_interval - P_res) / P_interval
                else:
                    linear_P = self.map[P_index][n_index]*(n_interval - n_res)/n_interval + self.map[P_index][n_index+1]*n_res/n_interval
                    linear_P_plus = self.map[P_index + 1][n_index] * (n_interval - n_res)/n_interval + self.map[P_index + 1][
                                   n_index + 1]*n_res/n_interval
                    FC = linear_P*(P_interval - P_res) / P_interval + linear_P_plus*P_res / P_interval
            return FC


    def OptimumCalc_non_rec(self, shape = _map_shape):
        m = int(shape[0]*shape[1]/3)
        # print(m)
        P = np.linspace(self.P_lowerbound, self.P_upbound, m)
        C_opt = [2000 for i in range(m)]
        # print("{")
        # print(self.P_upper_bounds)
        # print(self.P_lower_bounds)
        # print(self.map[6])
        # print(self.line_interp(8, np.array(self.map[6]),mode = 1))
        for k in range(m):
            for i in range(shape[1]):
                if self.P_upper_bounds[i]>= P[k] >=self.P_lower_bounds[i]:
                    yn = np.array(self.map[i])

                    temp = self.line_interp(P[k], yn)

                    if temp < C_opt[k]:
                        C_opt[k] = temp
                    if C_opt[k] < self.min_reduced_FC:
                        self.min_reduced_FC = C_opt[k]
        # plt.plot(P, C_opt)
        self.FC_opt = [P,C_opt]

        FC_temp = np.polyfit(P, C_opt, 18)
        self.FC_fit = FC_temp
        # 以下是画图部分
        # config = {
        #     "font.family": 'serif',
        #     "font.size": 16,
        #     "mathtext.fontset": 'stix',
        #     "font.serif": ['SimSun'],
        # }
        # plt.rcParams.update(config)
        # plt.plot(P, np.polyval(self.FC_fit, P))
        # plt.xlim(0,15)
        # plt.ylim(300,500)
        # plt.xlabel("功率 /kW",fontsize=14)
        # plt.ylabel("比油耗 /(g/kWh)",fontsize=14)
        # plt.show()


    def OptimumCalc(self, shape = _map_shape):
        P = np.linspace(self.P_lowerbound, self.P_upbound, shape[0])
        FC = np.zeros(shape[0])
        for row in range(shape[0]):
            FC[row] = min(self.map[row,:])
        FC_temp = np.polyfit(P, FC, 2)
        self.FC_fit = FC_temp

    def get_Opt_FC(self, P):  #根据事先拟合的曲线计算最低油耗
        return np.polyval(self.FC_fit, P)

    def get_Opt_FC_interp_online(self, P, shape= _map_shape): #在线插值
        C_opt = 2000
        for i in range(shape[1]):
            if self.P_upper_bounds[i] >= P>= self.P_lower_bounds[i]:
                yn = np.array(self.map[i])
                temp = self.line_interp(P, yn)
                if temp < C_opt:
                    C_opt = temp
        return C_opt

    def get_Opt_FC_DOUBLE_Interp(self, P):
        if self.P_lowerbound<P<self.P_upbound:

            cursor = 0
            while self.FC_opt[0][cursor]<P:
                cursor += 1

            temp = self.FC_opt[1][cursor]*(P - self.FC_opt[0][cursor-1])+self.FC_opt[1][cursor-1]*(self.FC_opt[0][cursor] - P)
            temp = temp/(self.FC_opt[0][cursor]-self.FC_opt[0][cursor-1])
            return temp
        else :
            print("P need out of range")
            return -1

    def fit_interp(self,x, yn):
        z = np.polyfit(yn[:,0], yn[:,1],13)
        val = np.polyval(z,x)
        return val

    def line_interp(self, x, yn , mode = 0):
        index = 0
        if x<yn[0][0] or x > yn[len(yn)-1][0]:
            temp = 0
        else:
            while x>yn[index][0]:
                index+=1
            if mode == 1:

                print("index = "+ str(index))
            if index < yn.shape[0]:
                # print(x)

                temp = (x - yn[index-1][0])*yn[index][1] + (yn[index][0] - x)*yn[index-1][1]


                temp = temp/(yn[index][0] - yn[index-1][0])

            else:
                temp = yn[index][1]
        return temp

    def get_min_reduced_FC(self):
        return self.min_reduced_FC

    def draw_contour(self):
        n = np.array(self.n_group)
        P = np.linspace(self.P_lowerbound, self.P_upbound, 30)
        n,p = np.meshgrid(n,P)
        print(n.shape[0])
        c = [[0 for i in range(P.shape[0])]for k in range(n.shape[0])]
        for i in range(n.shape[0]):
            for j in range(P.shape[0]):

                c[i][j] = self.line_interp(P[j], self.map[i])
        c = np.array(c)
        print(len(n))
        print(c.shape[1])
        # plt.contour(P,n,c, 16)
        fig = plt.figure()
        axec = Axes3D(fig)
        axec.scatter(P,n,c)

        plt.show()



test = OptimumFC()
test.import_map_bycol()
print("1")
print(test.get_Opt_FC(14.7))
# test.draw_contour()
