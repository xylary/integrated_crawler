import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.pylab import *

# Setting Chinese Font
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('data/lianjia/subdistrict_details_sh_20190223.csv', encoding='gbk')
df.subdistrict_xiaoqu_num = df.subdistrict_xiaoqu_num.astype(int)
group = df.groupby('district_name')
df1 = group.aggregate(np.sum)
df1.plot.bar()
plt.show()
df = df[df.subdistrict_xiaoqu_num <= 1000]
df[['subdistrict_name', 'subdistrict_xiaoqu_num']].plot.bar()
plt.show()
