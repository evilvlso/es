#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: handle_csv.py 
@time: 2019/04/23
@desc: 
    处理大csv
    根据分类category_one将大文件分为多个分类
    如果分类之后的文件还是很大，根据category_two分类
"""

import pandas as pd

df = pd.read_csv('51bushou/51bushou_母婴童装.csv', low_memory=False)
for i in df['category_two'].unique():
    if '/' in i:
        i = i.replace('/', '_')
    print(i)
    df[df.category_two == i].to_csv('51bushou/51bushou_母婴童装/51bushou_母婴童装_{}.csv'.format(i), encoding='utf-8-sig')

