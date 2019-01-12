#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : Yuri yuri@utohub.com
# @File    : middlewares.py

from scrapy import signals, Request
from scrapy.core.downloader.handlers.http11 import TunnelError
import requests
import time
import logging
from datetime import datetime

class ZhimaProxy(object):
    proxy = None

    def __init__(self, proxy_pool_api):
        self.proxy_pool_api = proxy_pool_api

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(
            proxy_pool_api=crawler.settings.get('PROXY_POOL', None),
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        spider.logger.info('Processing: {url}'.format(url=request.url))
        request.meta['proxy'] = self.get_proxy()
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        spider.logger.debug('Download success: {url}'.format(url=response.url))
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        if isinstance(exception, TunnelError):
            request.meta['retry_times'] = 0
            return request
        spider.logger.error('Download failed: %s' % request.url)

    def spider_opened(self, spider):
        pass

    def get_proxy(self):
        # get a proxy
        if self.proxy_pool_api is None:
            return None

        if self.proxy is None or self.is_expire(self.proxy['expire_time']):
            proxies = self.fetch_proxy(self.proxy_pool_api)
            if proxies is None or len(proxies) == 0:
                return None
            proxies = self.sort_proxies(proxies)
            self.proxy = proxies[-1]
        
        return 'http://{ip}:{port}'.format(ip=self.proxy['ip'], port=self.proxy['port'])

    def fetch_proxy(self, proxy_pool_api):
        # fetch proxies from proxy pool
        response = requests.get(proxy_pool_api)
        try:
            response.raise_for_status()
        except Exception as e:
            return None
        content = response.json()
        if content['success'] is False:
            logging.error('Fetch proxies failed, {message}'.format(message=content['msg']))
            return None
        proxies = content['data']
        return proxies
    
    def sort_proxies(self, proxies):
        # sort proxies by expire_time
        return sorted(proxies, key=lambda proxy:proxy['expire_time'])
    
    def is_expire(self, expire_datetime_string):
        # check whether proxy is expired
        now_timestamp = time.time()
        expire_timestamp = time.mktime(time.strptime(expire_datetime_string, "%Y-%m-%d %H:%M:%S"))
        return expire_timestamp - now_timestamp < 30