# -*- coding: utf-8 -*-

from PropellerCompt import PropellerComputation as ComptP
import numpy as np
import math
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class UAVpower:
    'G[N],h[m],Tem[0C],Bp[g]'
    def __init__(self, nr, G, Bp, h, Tem, Dprange = [0.1016,0.6858], Hprange = [0.0508,0.381]):
        self.nr = nr
        self.G = G
        self.T = G/nr
        self.h = h
        self.Tem = Tem
        self.Dprange = Dprange
        self.Hprange = Hprange
        self.Bp = Bp
        self.rho = self.__calc_rho()
        self.P = self.Pmap()
        print(self.P)

    def __calc_rho(self):
        temp = 1 - 0.0065*self.h/(273 + self.Tem)
        Pa = 101325*math.pow(temp, 5.2561)
        rho = 273*Pa*1.293/(101325*273 + self.Tem)
        return rho

    def Pmap(self):
        n_Dp = math.ceil((self.Dprange[1] - self.Dprange[0])/0.0127)
        n_Hp = math.ceil((self.Hprange[1] - self.Hprange[0])/0.0127)
        Dp_coordinate = [i * 0.0127 + self.Dprange[0] for i in range(n_Dp)]
        Hp_coordinate = [i * 0.0127 + self.Hprange[0] for i in range(n_Hp)]
        P = np.zeros((n_Dp, n_Hp))

        for coorDp, Dp in enumerate(Dp_coordinate):
            for coorHp, Hp in enumerate(Hp_coordinate):
                if Hp < Dp:
                    calc = ComptP(self.T, 10, self.rho, Dp, Hp, Bp=self.Bp)
                    P[coorDp][coorHp] = calc.get_P()
        return P

    def plot(self):
        figure = plt.figure()
        ax = Axes3D(figure)
        n_Dp = math.ceil((self.Dprange[1] - self.Dprange[0]) / 0.0127)
        n_Hp = math.ceil((self.Hprange[1] - self.Hprange[0]) / 0.0127)
        Dp_coordinate = [i * 0.0127 + self.Dprange[0] for i in range(n_Dp)]
        Hp_coordinate = [i * 0.0127 + self.Hprange[0] for i in range(n_Hp)]
        X, Y = np.meshgrid(Hp_coordinate, Dp_coordinate)
        print(self.P.shape)
        print(X)
        print(Y)
        ax.plot_surface(X, Y, self.P, rstride=1, cstride=1, cmap='rainbow')
        ax.set_xlabel(r"Hp(m)")
        ax.set_ylabel(r"Dp(m)")
        ax.set_zlabel(r"P(w)")
        plt.show()

    # def plot_


test = UAVpower(4,800,2,200,20,[0.7,0.9],[0.3, 0.4])
test.plot()