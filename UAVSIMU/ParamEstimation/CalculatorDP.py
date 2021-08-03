# -*- coding: utf-8 -*-
# 根据片段的DP计算 #
# 简化计算，将发动机功率离散为[1,15kw]间的100个点，计算每个时间步上的总能量损失 #
# 损失函数：计算每个时间步上的总#

import matplotlib.pyplot as plt
from scipy import signal
from ControlEfficiencyModel import static_model
import xlrd
import random
import pandas as pd
import os

class DP_calculator:
    def __init__(self):
        self.initState = []
        self.endState = []

