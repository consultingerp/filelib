# -*-coding:utf-8-*-
import logging
import time

import requests
from requests.compat import json as _json
from wechatpy.constants import WeChatErrorCode
from werobot.client import Client
from werobot.client import check_error

logger = logging.getLogger(__name__)


class WxClient(Client):

    def request(self, method, url, **kwargs):
        if "params" not in kwargs:
            kwargs["params"] = {"access_token": self.token}
        if isinstance(kwargs.get("data", ""), dict):
            body = _json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(method=method, url=url, **kwargs)
        r.raise_for_status()
        r.encoding = "utf-8"
        json = r.json()
        if 'errcode' in json:
            json['errcode'] = int(json['errcode'])

        if 'errcode' in json and json['errcode'] != 0:
            errcode = json['errcode']
            errmsg = json.get('errmsg', errcode)
            if errcode in (
                    WeChatErrorCode.INVALID_CREDENTIAL.value,
                    WeChatErrorCode.INVALID_ACCESS_TOKEN.value,
                    WeChatErrorCode.EXPIRED_ACCESS_TOKEN.value):
                logger.info('Access token expired, fetch a new one and retry request')
                self.session.delete(self.access_token_key)
                self.get_access_token()
                access_token = self.session.get(self.access_token_key)
                logger.info('get new token %s' % access_token)
                kwargs["params"] = {"access_token": access_token}
                return super(WxClient, self).request(method=method, url=url, **kwargs)
            else:
                if check_error(json):
                    return json
        if check_error(json):
            return json

    def get_access_token(self):
        """
        重写有保存token

        :return: 返回token
        """
        self.token_expires_at = self.session.get(self.access_token_key_expires_at)
        self._token = self.session.get(self.access_token_key)
        if self._token and self.token_expires_at:
            now = time.time()
            if self.token_expires_at - now > 60:
                return self._token
        json = self.grant_token()
        self._token = json["access_token"]
        self.token_expires_at = int(time.time()) + json["expires_in"]
        self.session.set(self.access_token_key, self._token)
        self.session.set(self.access_token_key_expires_at, self.token_expires_at)
        return self._token

    @property
    def access_token_key(self):
        return '{0}_access_token'.format(self.appid)

    @property
    def access_token_key_expires_at(self):
        return '{0}_access_token__expires_at'.format(self.appid)
