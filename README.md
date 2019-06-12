## 每日一淘
* 接口:小程序接口
* 定时任务: 每天八点爬取全类(大约3+小时)
* 所在服务器: 10.6.50.92
* 程序重载: `bash code_reload`
* crontab:
```bash
0 8 * * * source /etc/profile && cd /home/jenkins/mryitao/scrapy_fish && /usr/bin/python3 -u add_task.py add_category >> /home/jenkins/mryitao/add_category.log 2>&1
```
---
## 接口如下
## 分类
```angular2html
curl -H 'Host: api.mryitao.cn' -H 'accept: */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-language: zh-cn' -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN' -H 'referer: https://servicewechat.com/wxeb45228be3146ddc/90/page-frame.html' --data-binary "{}" --compressed 'https://api.mryitao.cn/api/marketing/classification/firstList?p=wxapp&v=4.6.4&tk=RldCTThqY0JWVUZWdDZ4YzVEUlBHUDJIZ0h1a2JGMlVzRnNrZEVaTTJNaz0%3D&sh=624&sw=414&mt=iPhone%207%20Plus%3CiPhone9%2C2%3E
```
## 二级
```angular2html
curl -H 'Host: api.mryitao.cn' -H 'accept: */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-language: zh-cn' -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN' -H 'referer: https://servicewechat.com/wxeb45228be3146ddc/90/page-frame.html' --data-binary '{"firstId":4}' --compressed 'https://api.mryitao.cn/api/marketing/classification/secondList?p=wxapp&v=4.6.4&tk=RldCTThqY0JWVUZWdDZ4YzVEUlBHUDJIZ0h1a2JGMlVzRnNrZEVaTTJNaz0%3D&sh=624&sw=414&mt=iPhone%207%20Plus%3CiPhone9%2C2%3E
```

## ITEMS
```angular2html
curl -H 'Host: api.mryitao.cn' -H 'accept: */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-language: zh-cn' -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN' -H 'referer: https://servicewechat.com/wxeb45228be3146ddc/90/page-frame.html' --data-binary '{"pageNo":0,"pageSize":20,"bindCatelogIds":["574","594"],"secondId":"77"}' --compressed 'https://api.mryitao.cn/api/marketing/classification/getClassifyProductList?p=wxapp&v=4.6.4&tk=RldCTThqY0JWVUZWdDZ4YzVEUlBHUDJIZ0h1a2JGMlVzRnNrZEVaTTJNaz0%3D&sh=624&sw=414&mt=iPhone%207%20Plus%3CiPhone9%2C2%3E
```

## sku
```angular2html
curl -H 'Host: api.mryitao.cn' -H 'accept: */*' -H 'content-type: application/json;charset=UTF-8' -H 'accept-language: zh-cn' -H 'user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN' -H 'referer: https://servicewechat.com/wxeb45228be3146ddc/90/page-frame.html' --data-binary '{"sku":"100717364","address":null}' --compressed 'https://api.mryitao.cn/api/product/v4/productDetail?p=wxapp&v=4.6.4&tk=RldCTThqY0JWVUZWdDZ4YzVEUlBHUDJIZ0h1a2JGMlVzRnNrZEVaTTJNaz0%3D&sh=624&sw=414&mt=iPhone%207%20Plus%3CiPhone9%2C2%3E
```

