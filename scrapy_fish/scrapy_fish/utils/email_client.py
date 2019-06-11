#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@author: zhangslob 
@file: email_client.py
@time: 2019/05/14
@desc: 
    发送邮件

    发送html正文方法：https://python-book.readthedocs.io/zh_CN/latest/libs/exchangelib.html#html
"""
from .get_logger import get_logger
from exchangelib import ServiceAccount, Account, DELEGATE
from exchangelib import Message, Mailbox, FileAttachment


class PyEmail(object):
    def __init__(self, user='licaiops', password='y6bv4L8tP0pAKoL0'):
        self.logger = get_logger(name='email_client', file=False)
        credentials = ServiceAccount(username=user, password=password)
        self.account = Account(primary_smtp_address='{}@blackfish.cn'.format(user),
                               credentials=credentials,
                               autodiscover=True, access_type=DELEGATE)
        self.logger.info('start send_email')

    def send_email(self, subject, body, addressee, attachments=None):
        """
        Send an email.

        Parameters
        ----------
        subject : str 主题
        body : str 正文
        addressee : list
            Each str is and email address
        attachments : list of tuples or None
            filepath
        """
        to_recipients = []
        for recipient in addressee:
            to_recipients.append(Mailbox(email_address=recipient))
        # Create message
        m = Message(account=self.account,
                    folder=self.account.sent,
                    subject=subject,
                    body=body,
                    to_recipients=to_recipients)

        # attach files
        for i in attachments or []:
            with open(i, 'rb') as f:
                file = FileAttachment(name=i.split('/')[-1], content=f.read())
                m.attach(file)
        m.send_and_save()
        self.logger.info('success send email to {}'.format('&'.join(addressee)))


if __name__ == '__main__':
    PyEmail().send_email(subject='每日竞争力报告-有优势', body='body', addressee=['slobzhang@blackfish.cn'],
                         attachments=['/Users/zhangslob/work/scrapy_fish/scrapy_fish/scrapy_fish/utils/base_crawler.py',
                                      '/Users/zhangslob/work/scrapy_fish/scrapy_fish/scrapy_fish/middlewares.py'])
