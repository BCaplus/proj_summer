# -*- coding: utf-8 -*-


import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy

x = [10,15,20,25,30]
y1 = [1.9,2.1,2.3,2.5,2.7]
y2 = [2.2,2.3,2.5,2.75,2.85]
y3 = [1.7,1.9,2.1,2.3,2.6]
y4 =[3.3,3.6,4,4.4,4.9]
y5=[3.45,3.9,4.3,4.7,5.2]
y6=[3.3,3.7,	4.1,	4.6,	5]
y7=[4.6	,5.2	,5.8	,6.5	,7.3]
y8=[4.9	,5.5	,6.1	,6.8	,7.6]
y9=[4.9	,5.5	,6.2	,7	,7.7]

config = {
    "font.family":'serif',
    "font.size": 20,
    "mathtext.fontset":'stix',
    "font.serif": ['SimSun'],
}
rcParams.update(config)

plt.plot(x, y1, label = 'T=2000s, Mbat = 1',linestyle = '-',color = "green")
plt.plot(x, y4, label = 'T=3800s, Mbat = 1',linestyle = '-',color = "black")
plt.plot(x, y7, label = 'T=5600s, Mbat = 1',linestyle = '-',color = "red")
plt.plot(x, y2, label = 'T=2000s, Mbat = 3',linestyle = '--',color = "green")
plt.plot(x, y5, label = 'T=3800s, Mbat = 3',linestyle = '--',color = "black")
plt.plot(x, y8, label = 'T=5600s, Mbat = 3',linestyle = '--',color = "red")
plt.plot(x, y3, label = 'T=2000s, Mbat = 7',linestyle = ':',color = "green")
plt.plot(x, y6, label = 'T=3800s, Mbat = 7',linestyle = ':',color = "black")
plt.plot(x, y9, label = 'T=5600s, Mbat = 7',linestyle = ':',color = "red")

plt.ylabel('最小油耗/ kg', fontdict={'family' : 'simsun', 'size'   : 14})
plt.xlabel('载重/ kg', fontdict={'family' : 'simsun', 'size'   : 14})
plt.yticks(fontproperties = 'Times New Roman', size = 12)
plt.xticks(fontproperties = 'Times New Roman', size = 12)
plt.legend(loc=0,ncol=2,fontsize=10)
plt.show()