# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import FuncFormatter
import numpy

x = [10,15,20,25,30]
y1 = [1.9,2.1,2.3,2.5,2.7]
y1 = [y1[item]/(2000*x[item]) for item in range(len(y1))]
y2 = [2.2,2.3,2.5,2.75,2.85]
y2 = [y2[item]/(2000*x[item]) for item in range(len(y1))]
y3 = [1.7,1.9,2.1,2.3,2.6]
y3 = [y3[item]/(2000*x[item]) for item in range(len(y1))]
y4 =[3.3,3.6,4,4.4,4.9]
y4 = [y4[item]/(3800*x[item]) for item in range(len(y1))]
y5=[3.45,3.9,4.3,4.7,5.2]
y5 = [y5[item]/(3800*x[item]) for item in range(len(y1))]
y6=[3.3,3.7,	4.1,	4.6,	5]
y6 = [y6[item]/(3800*x[item]) for item in range(len(y1))]
y7=[4.6	,5.2	,5.8	,6.5	,7.3]
y7 = [y7[item]/(5600*x[item]) for item in range(len(y1))]
y8=[4.9	,5.5	,6.1	,6.8	,7.6]
y8 = [y8[item]/(5600*x[item]) for item in range(len(y1))]
y9=[4.9	,5.5	,6.2	,7	,7.7]
y9 = [y9[item]/(5600*x[item]) for item in range(len(y1))]

z1 = [y1[0], y4[0],y7[0]]
z2 = [y2[0], y5[0],y8[0]]
z3 = [y3[0], y6[0],y9[0]]

z4 = [y1[2], y4[2],y7[2]]
z5 = [y2[2], y5[2],y8[2]]
z6 = [y3[2], y6[2],y9[2]]

z7 = [y1[4], y4[4],y7[4]]
z8 = [y2[4], y5[4],y8[4]]
z9 = [y3[4], y6[4],y9[4]]

k = [2000,3800,5600]
plt.rcParams['font.sans-serif']=['FangSong']
# plt.rcParams['font.sans-serif']=['Times New Roman']
# plt.plot(x, y1, label = 'T=2000s, Mbat = 1',linestyle = '-')
# plt.plot(x, y4, label = 'T=3800s, Mbat = 1',linestyle = '-')
# plt.plot(x, y7, label = 'T=5600s, Mbat = 1',linestyle = '-')
# plt.plot(x, y2, label = 'T=2000s, Mbat = 3',linestyle = '--')
# plt.plot(x, y5, label = 'T=3800s, Mbat = 3',linestyle = '--')
# plt.plot(x, y8, label = 'T=5600s, Mbat = 3',linestyle = '--')
# plt.plot(x, y3, label = 'T=2000s, Mbat = 7',linestyle = ':')
# plt.plot(x, y6, label = 'T=3800s, Mbat = 7',linestyle = ':')
# plt.plot(x, y9, label = 'T=5600s, Mbat = 7',linestyle = ':')

plt.plot(k, z1, label = '载重10kg, Mbat = 1',linestyle = '-',color= "r")
plt.plot(k, z4, label = '载重20kg, Mbat = 1',linestyle = '-',color= "purple")
plt.plot(k, z7, label = '载重30kg, Mbat = 1',linestyle = '-',color= "b")
plt.plot(k, z2, label = '载重10kg, Mbat = 3',linestyle = '--',color= "r")
plt.plot(k, z5, label = '载重20kg, Mbat = 3',linestyle = '--',color= "purple")
plt.plot(k, z8, label = '载重30kg, Mbat = 3',linestyle = '--',color= "b")
plt.plot(k, z3, label = '载重10kg, Mbat = 7',linestyle = ':',color= "r")
plt.plot(k, z6, label = '载重20kg, Mbat = 7',linestyle = ':',color= "purple")
plt.plot(k, z9, label = '载重30kg, Mbat = 7',linestyle = ':',color= "b")

ax = plt.gca()
plt.xlim(2000,6000)
ax.xaxis.set_major_locator(FixedLocator(k))

def formatnum(x, pos):
    return '$%.1f$x$10^{-4}$' % (x*10000)
formatter = FuncFormatter(formatnum)
ax.yaxis.set_major_formatter(formatter)
plt.ylabel('单位时间比油耗/ (kg 燃料/s·kg 载重)',fontdict={'family' : 'simsun', 'size'   : 14})
plt.xlabel('飞行时间/ s',fontdict={'family' : 'simsun', 'size'   : 14})
plt.yticks(fontproperties = 'Times New Roman', size = 12)
plt.xticks(fontproperties = 'Times New Roman', size = 12)
# plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
plt.legend(loc=0,ncol=2)
plt.show()