from utils.pipeline import *


'''
sh_xiaoqu = get_xiaoqu_list('sh')
print(sh_xiaoqu)
'''


xiaoqu_url = 'https://sh.lianjia.com/xiaoqu/5011000016470/'
info = get_xiaoqu_detailed_info(xiaoqu_url)
print()