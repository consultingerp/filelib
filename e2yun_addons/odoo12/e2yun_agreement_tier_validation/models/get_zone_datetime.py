#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    import pytz
    import datetime
except BaseException as b:
    pass

class GetDatetime():
    def get_datetime(self,timezone=False):
        if timezone:
            tz = pytz.timezone(timezone)
        else:
            tz = pytz.timezone('Asia/Shanghai')
        time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return time

