import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import pandas as pd


font_path = "C:\Windows\Fonts\微软雅黑\微软雅黑 常规.ttf"
prop = mfm.FontProperties(fname=font_path)
plt.text(0.5, 0.5, s=u'测试', fontproperties=prop)
plt.show()

# df = pd.read_csv('subdistrict_details_sh_20190223.csv')
