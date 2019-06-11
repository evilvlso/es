#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: send_mail.py
@time: 2019/04/25
@desc: 
    发送邮件
    线上环境可以用
"""  

import requests


def send_email(subject='邮件主题', addressee='slobzhang@blackfish.cn', body='正文', attachment='附件'):
    """
    发送邮件
    :param subject: 邮件主题
    :param addressee: 收件人（多个：'zihaodeng@blackfish.cn,scottshi@blackfish.cn'）
    :param body: 正文
    :param attachment: 附件，文件位置，多个文件同样用','连接
    :return:
    """
    url = 'http://localhost:8080/shopping-data-analysis/mail/send'

    data = {
        'subject': subject,
        'addressee': addressee,
        'body': body,
        'attachment': attachment
    }

    resp = requests.post(url, data=data)
    print(resp.json())
