#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
import random
import matplotlib as plot
import math


# 变量命名：类和函数内均为下划线命名法，其余为驼峰命名

def fit_func(pos, Body = [1.2192, 12.192, 0.3]):  # 评估函数
    result, xcp = get_result(pos, Body)
    f = 4/7*(result[0]/result[1]) + 3/7*(1/result[1])  # 在确定质心和差值函数的情况下还应计算静态裕量
    return f

class Particle:
    def __init__(self, upper_range, lower_range, max_vel, dim):
        self.__pos = [random.uniform(lower_range[i], upper_range[i]) for i in range(dim)]  # 粒子的位置
        self.__vel = [random.uniform(-max_vel, max_vel) for i in range(dim)]  # 粒子的速度
        self.__bestPos = [0.0 for i in range(dim)]  # 粒子最优位置
        self.__fitnessValue = fit_func(self.__pos)  # 适应度函数值

#对于实验性的情况，规定dim[0]存储fin cord, dim[1]存储fin_span, dim[2]存储前掠角



    def set_pos(self, i, value):
        self.__pos[i] = value

    def get_pos(self):
        return self.__pos

    def set_best_pos(self, i, value):
        self.__bestPos[i] = value

    def get_best_pos(self):
        return self.__bestPos

    def set_vel(self, i, value):
        self.__vel[i] = value

    def get_vel(self):
        return self.__vel

    def set_fitness_value(self, value):
        self.__fitnessValue = value

    def get_fitness_value(self):
        return self.__fitnessValue


class PSO:
    def __init__(self, dim, size, iter_num, upper_range, lower_range, max_vel, Body, best_fitness_value = float('Inf'), C1 = 2, C2 = 1, W = 1, a_PSO = 0.3, epsilon = 1e-6):
        self.C1 = C1 # particle学习因子
        self.C2 = C2 # swarm学习因子
        self.W = [[W for j in range(dim)]for i in range(size)] # 初始化惯性
        self.dim = dim # 维度
        self.size = size # 粒子数
        self.fit_func = fit_func # fit函数缺省值
        self.iter_num = iter_num  # 迭代次数
        self.upper_range = upper_range # 域（方形）上界
        self.lower_range = lower_range # 域下界
        self.max_vel = max_vel  # 粒子最大速度
        self.body = Body # 弹体参数
        self.best_fitness_value = best_fitness_value #需要多次迭代时上一次迭代的结果作为这一次的初始值以节省时间
        self.best_position = [0.0 for i in range(dim)]  # 种群最优位置
        self.fitness_val_list = []  # 每次迭代最优适应值
        self.a_PSO = a_PSO #自适应权重参数
        self.epsilon = epsilon #个体搜索值参数

        # 对种群进行初始化
        self.Particle_list = [Particle(self.upper_range, self.lower_range, self.max_vel, self.dim) for i in range(self.size)]

        def set_bestFitnessValue(self, value):
            self.best_fitness_value = value

        def get_bestFitnessValue(self):
            return self.best_fitness_value

        def set_bestPosition(self, i, value):
            self.best_position[i] = value

        def get_bestPosition(self):
            return self.best_position

        # 更新自适应惯性值
        def update_w(self, part):
            Weight = [1 for i in range(self.dim)]
            for j in range(self.dim):
                numerator = abs(part.get_pos()[j] - part.get_best_pos()[j])
                denominator = abs(part.get_best_pos()[j] - self.get_bestPosition()[j]) + self.epsilon
                ISA = numerator/denominator
                Weight[j] = 1 - self.a_PSO/(1 + math.exp(-ISA))
            self.w = Weight

        # 更新速度
        def update_vel(self, part):
            weight = self.update_w(part)
            for i in range(self.dim):
                vel_value = weight[i] * part.get_vel()[i] + self.C1 * random.random() * (part.get_best_pos()[i] - part.get_pos()[i]) \
                            + self.C2 * random.random() * (self.get_bestPosition()[i] - part.get_pos()[i])
                if vel_value > self.max_vel:
                    vel_value = self.max_vel
                elif vel_value < -self.max_vel:
                    vel_value = -self.max_vel
                part.set_vel(i, vel_value)

        # 更新位置
        def update_pos(self, part):
            for i in range(self.dim):
                pos_value = part.get_pos()[i] + part.get_vel()[i]
                part.set_pos(i, pos_value)
            value = fit_func(part.get_pos())
            if value < part.get_fitness_value():
                part.set_fitness_value(value)
                for i in range(self.dim):
                    part.set_best_pos(i, part.get_pos()[i])
            if value < self.get_bestFitnessValue():
                self.set_bestFitnessValue(value)
                for i in range(self.dim):
                    self.set_bestPosition(i, part.get_pos()[i])
        # 进行一次Opt并输出结果
        def update(self):
            for i in range(self.iter_num):
                for part in self.Particle_list:
                    self.update_vel(part)  # 更新速度
                    self.update_pos(part)  # 更新位置
                self.fitness_val_list.append(self.get_bestFitnessValue())  # 每次迭代完把当前的最优适应度存到列表
            return self.fitness_val_list, self.get_bestPosition()



