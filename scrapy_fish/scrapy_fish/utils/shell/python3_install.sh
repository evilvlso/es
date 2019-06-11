#!/usr/bin/env bash
#安装EPEL依赖
sudo yum install -y epel-release

#安装IUS软件源
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo  yum makecache
sudo yum install -y python36u

sudo ln -s /bin/python3.6 /bin/python3

sudo yum install -y python36u-pip

sudo ln -s /bin/pip3.6 /bin/pip3