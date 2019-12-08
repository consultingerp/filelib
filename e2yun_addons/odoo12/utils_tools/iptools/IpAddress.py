# -*- coding: utf-8 -*-
#  获取用户地址对应的地区


import logging
import requests
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class IpAddress():

    def __init__(self):
        super(IpAddress, self).__init__()

    @classmethod
    def getregion(cls, userip):
        url = "http://ip138.com/ips138.asp"
        ip_check = {'ip': userip}
        ipresult = requests.request('GET', url, params=ip_check)
        ipresult.encoding = 'gbk'
        iphtml = ipresult.text
        soup = BeautifulSoup(iphtml, "html.parser")
        soup = soup.ul
        ipinfo = {}
        if soup:
            region_user = soup.contents[0].string[5:7]
            ipinfo['ip'] = userip
            ipinfo['region'] = region_user
            _logger.info("地区：%s:%s" % (userip, region_user))
            info = soup.contents[0].string[5:]
            ipinfo['info'] = info
            _logger.info("查询接口1：%s", ipinfo)
            info1 = soup.contents[1].string[6:]
            ipinfo['info1'] = info1
            _logger.info("查询接口2：%s", info1)
            info2 = soup.contents[2].string[6:]
            ipinfo['info2'] = info2
            _logger.info("查询接口3：%s", info2)
        return ipinfo
