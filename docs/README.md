# Scrapy_fish

# 基本使用

### 第一步clone自己的项目

`git clone http://slobzhang@git.blackfi.sh/scm/~slobzhang/youhaodongxi.git`

### 第二步添加scrapy_fish 源

`git remote add scrapy_fish http://slobzhang@git.blackfi.sh/scm/~slobzhang/scrapy_fish.git`

### 第三步拉取模板代码

`git fetch scrapy_fish`

### 第四步将模板代码合并到当前分支

```
git merge scrapy_fish/master

# 如果出现 fatal: refusing to merge unrelated histories，则使用
git merge scrapy_fish/master  --allow-unrelated-histories
```

### 第五步第一次上传代码

```bush
git add filename （若有多个文件，以空格分开）
git commit -m '第一次提交'
git push origin develop
```

------

# 继承Spider

有四个spider可以继承：

1. Spider:scrapy.spiders.Spider
2. CrawlSpider:scrapy.spiders.CrawlSpider
3. SpiderRedis:scrapy_redis.spiders.RedisSpider
4. CrawlSpiderRedis:scrapy_redis.spiders.CrawlSpiderRedis

所有爬虫必须从以上爬虫继承，如：

```python
from ..utils.base_crawler import Spider


class ExampleSpider(Spider):
    pass
```



# 每个爬虫的配置

用法：

```python

from ..utils.base_crawler import Spider
from ..utils.spider_settings import CustomSettings


class ExampleSpider(Spider):
    name = 'example'
    start_urls = []

    c = CustomSettings()
    c.EnProxy = True
    c.EnRedis = True
    c.EnSaveHtml = False
    c.EnFakeUserAgent = False
    c.LOG_LEVEL_CUS = 'INFO'
    c.RETRY_TIMES_CUS = 15
    c.DOWNLOAD_TIMEOUT_CUS = 20
    c.COOKIES_ENABLED_CUS = False
    c.CONCURRENT_REQUESTS_CUS = 100
    c.REDIS_START_URLS_AS_SET_CUS = True

    c.RETRY_HTTP_CODES_CUS = list(range(400, 600))

    c.ITEM_PIPELINES_CUS = {
        # 'scrapy_zs.pipelines.MongoDBPipeline': 305,
    }
    custom_settings = c()
```

如需要增加自定义设置，添加并在末尾加上`_CUS`即可。



# 开发环境配置

统一从`scrapy_fish/scrapy_fish/utils/settings_.py`导入，如

```python
from .utils.settings_ import *
```

已经有MongoDB、MySQL、RabbitMQ的连接：`mongo_client`和`mysql_client`和`pika_client`

> 注意MySQL的默认连接cursorclass是`pymysql.cursors.DictCursor`

爬虫中有其他地方需要使用的，直接从此处导入，无需再次声明，使用之后请关闭连接。



# 安装包版本

根目录下运行`pip3 install -r require/requirements.txt`

> 因为pika的版本必须是0.13.0

# 文件介绍

目录：`scrapy_fish/scrapy_fish/scrapy_fish/utils`

```bash
➜  utils git:(master) ✗ tree
├── base_crawler.py     # 所有爬虫必须从此继承
├── date_.py            # 获取时间的基本格式
├── dingtalk.py					# 发送钉钉消息
├── handle_csv.py				# 按种类分割大csv文件
├── items_.py						# items示例文件
├── middlewares_.py			# 中间件示例文件
├── pipelines_.py				# 中间件示例文件
├── send_mail.py				# 发送邮件示例文件
├── settings_.py				# 开发富案件设置
└── spider_settings.py	# 爬虫设置文件

```



