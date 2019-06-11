FROM zhangslob/base:latest

LABEL maincontain=mryitao
COPY localtime /etc/
COPY ./requirements.txt /root/app/requirements.txt
RUN pip3 --no-cache-dir install -r /root/app/requirements.txt -i https://pypi.douban.com/simple

COPY ./scrapy_fish /root/app/
WORKDIR /root/app/scrapy_fish/


CMD ["scrapy","crawl","mryitao"]