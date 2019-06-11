#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@author: zhangslob 
@file: py_md5.py 
@time: 2019/05/22
@desc: 
    
"""  

import hashlib


def md5_str(txt):
    m = hashlib.md5(txt.encode(encoding='utf-8'))
    return m.hexdigest()


# if __name__ == '__main__':
#     print(md5_str('1231'))
