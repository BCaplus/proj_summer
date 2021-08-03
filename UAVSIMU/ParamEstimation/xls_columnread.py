#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt
import csv
import xlrd

def read_bycolumn():
    Nc = 13
    group_curve = []
    n_group = []
    Raw = xlrd.open_workbook("Engine Map 2.xls")
    sh = Raw.sheet_by_name("Sheet2")
    k = 0
    lower_p_bound = []
    upper_p_bound = []
    while k < sh.ncols:
        col = [str(sh.cell_value(i, k)) for i in range(0, sh.nrows)]
        if "rpm" in col[0]:
            temp = str(col[0])
            temp = temp.replace('rpm','',1)
            # print(temp)
            n_group.append(float(temp))
            p_col = [str(sh.cell_value(i, k+2)) for i in range(1, sh.nrows)]

            p_col = [float(p_col[i]) for i in range(len(p_col)) if p_col[i] != '']
            # print(p_col)
            F_col = [str(sh.cell_value(i, k+3)) for i in range(1, sh.nrows)]
            F_col = [float(F_col[i]) for i in range(len(F_col)) if F_col[i] != '']
            # print(F_col)
            temp_group = []
            for j in range(len(p_col)):
                temp_group.append([p_col[j], F_col[j]])
            temp_group = np.array(temp_group)
            temp_group = temp_group[temp_group[:, 0].argsort()]
            group_curve.append(temp_group)
            # print(k)

            cursor = 0
            while cursor < len(temp_group) and temp_group[cursor+1, 0] - temp_group[cursor, 0]>4:
                cursor += 1
            lower_p_bound.append(temp_group[cursor,0])
            upper_p_bound.append(temp_group[len(temp_group)-1,0])
            plt.scatter(temp_group[:, 0], temp_group[:, 1])
            k= k + 3

        else:
            k= k + 1

    group_curve = np.array(group_curve)
    return [group_curve, n_group, upper_p_bound, lower_p_bound]

read_bycolumn()