# Zhima Proxy
A scrapy downloader middleware for proxing bandwidth to [zhimahttp](http://h.zhimaruanjian.com/).

## Usage

### First step, copy zhima_proxy folder to your project

### Second step, generate a API
Navigate to [zhimahttp](http://h.zhimaruanjian.com/) and get a personal API(json format with expire time).

### Third step, configuration
To activate this middleware it needs to be added to the SPIDER_MIDDLEWARES dict, i.e:
```
# In settings.py
SPIDER_MIDDLEWARES = {
    'zhima_proxy.ZhimaProxy': 543,
}
```

`PROXY_POOL`

Your API generated by [zhimahttp](http://h.zhimaruanjian.com/), i.e:
```
# In settings.py
PROXY_POOL = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=11&pack=xxx&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
```