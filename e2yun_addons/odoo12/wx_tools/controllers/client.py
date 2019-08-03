# coding=utf-8
import logging
import time

import redis
from wechatpy.client import WeChatClient
from wechatpy.client.api.jsapi import WeChatJSAPI
from wechatpy.component import ComponentOAuth
from wechatpy.oauth import WeChatOAuth
from wechatpy.session.memorystorage import MemoryStorage
from wechatpy.session.redisstorage import RedisStorage
from wechatpy.utils import random_string
from werobot.client import ClientException
from werobot.logger import enable_pretty_logging

from odoo import exceptions
from odoo import fields
from ..basewechat.base import EntryBase
from ..basewechat.werobot import WeRoBot

_logger = logging.getLogger(__name__)

WxEnvDict = {}


class WxEntry(EntryBase):

    def __init__(self):
        robot = WeRoBot()
        robot.config["APP_ID"] = ""
        robot.config["APP_SECRET"] = ""
        self.wxclient = robot.client
        self.wechatpy_client = None
        self.robot = None
        self.subscribe_auto_msg = None

        # 微信 CODE
        self.WX_CODE = {}

        super(WxEntry, self).__init__()

    def init(self, env):
        dbname = env.cr.dbname
        global WxEnvDict
        if dbname in WxEnvDict:
            del WxEnvDict[dbname]
        WxEnvDict[dbname] = self

        try:
            config = env['wx.config'].sudo().get_cur()
            action = config.action
        except:
            import traceback;
            traceback.print_exc()
            action = None
        if action:
            self.subscribe_auto_msg = config.action.get_wx_reply()

        Param = env['ir.config_parameter'].sudo()
        self.wx_token = Param.get_param('wx_token') or ''
        self.wx_appid = Param.get_param('wx_appid') or ''
        self.wx_AppSecret = Param.get_param('wx_AppSecret') or ''
        self.server_url = Param.get_param('server_url') or ''
        self.session_storage = Param.get_param('session_storage') or ''
        # robot.config["TOKEN"] = self.wx_token
        # self.wxclient.appid = self.wx_appid
        # self.wxclient.appsecret = self.wx_AppSecret
        self.wxclient.config["APP_ID"] = self.wx_appid
        self.wxclient.config["APP_SECRET"] = self.wx_AppSecret
        self.wxclient.config["server_url"] = self.server_url

        if not self.session_storage:
            session_storage = MemoryStorage()
            _logger.info("启用MemoryStorage")
        else:
            _logger.info("启用RedisStorage%s" % self.wx_appid)
            db = redis.Redis(host=self.session_storage, port=6379)
            session_storage = RedisStorage(db, prefix=self.wx_appid)
        try:
            #  获取以前的token是否需要获取新的Token AccessToken
            self.wxclient.session = session_storage
            # self.wxclient._token = session_storage.get(self.access_token_key)
            _ = self.wxclient.token
        except Exception as e:
            print(e)
            import traceback;
            traceback.print_exc()
            _logger.error(u'初始化微信客户端token失败，请在微信对接配置中填写好相关信息！')

        robot = WeRoBot(token=self.wx_token, enable_session=True, logger=_logger, session_storage=session_storage)
        enable_pretty_logging(robot.logger)
        self.robot = robot
        try:
            wechatpy_client = WeChatClient(self.wx_appid, self.wx_AppSecret, access_token=self.wxclient.token,
                                           session=session_storage)
            self.wechatpy_client = wechatpy_client
        except Exception as e:
            print(e)
            _logger.error("加载微信token错误。")
        try:
            users = env['wx.user'].sudo().search([('last_uuid', '!=', None)])
            for obj in users:
                if obj.last_uuid_time:
                    self.recover_uuid(obj.openid, obj.last_uuid, fields.Datetime.from_string(obj.last_uuid_time))
        except:
            env.cr.rollback()
            import traceback;
            traceback.print_exc()
        print('wx client init: %s %s' % (self.OPENID_UUID, self.UUID_OPENID))

    @property
    def access_token_key(self):
        return '{0}_access_token'.format(self.wxclient.appid)

    def send_text(self, openid, text):
        try:
            self.wxclient.send_text_message(openid, text)
        except ClientException as e:
            raise exceptions.UserError(u'发送失败 %s' % e)

    def chat_send(self, uuid, msg):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.send_text(openid, msg)

    def upload_media(self, media_type, media_file):
        try:
            return self.wxclient.upload_media(media_type, media_file)
        except ClientException as e:
            if str(e).find('40004') >= 0:
                raise exceptions.UserError('不合法的媒体文件类型，支持PNG,JPEG,JPG,GIF,AMR,MP3,MP4')
            elif str(e).find('40005') >= 0:
                raise exceptions.UserError('不合法的文件类型，支持PNG,JPEG,JPG,GIF,AMR,MP3,MP4')
            elif str(e).find('40006') >= 0:
                raise exceptions.UserError('不合法的文件大小2M以内')
            elif str(e).find('40009') >= 0:
                raise exceptions.UserError('不合法的图片文件大小2M以内')
            elif str(e).find('40010') >= 0:
                raise exceptions.UserError('不合法的语音文件大小2M以内')
            elif str(e).find('40011') >= 0:
                raise exceptions.UserError('不合法的视频文件大小10M以内')
            else:
                raise exceptions.UserError(u'image上传失败 %s' % e)

    def send_image_message(self, openid, media_id):
        try:
            self.wxclient.send_image_message(openid, media_id)
        except ClientException as e:
            raise exceptions.UserError(u'发送image失败 %s' % e)

    def send_image(self, uuid, media_id):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.send_image_message(openid, media_id)

    def send_voice(self, uuid, media_id):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            try:
                self.wxclient.send_voice_message(openid, media_id)
            except ClientException as e:
                raise exceptions.UserError(u'发送voice失败 %s' % e)

    def get_jsapi_ticket(self, url):
        us_client = self.wechatpy_client
        jsapi = WeChatJSAPI(us_client)
        tick = jsapi.get_jsapi_ticket()
        noncestr = random_string()
        timestamp = str(int(time.time()))
        signature = jsapi.get_jsapi_signature(noncestr, tick, timestamp, url)
        return self.wx_appid, timestamp, noncestr, signature


def wxenv(env):
    return WxEnvDict[env.cr.dbname]


def send_template_message(self, user_id, template_id, data, url='', state='', url_type='in'):
    entry = wxenv(self.env)
    wxclient = entry.wxclient
    if url_type == 'USER':  # 用户URL 直接 转到URL
        url = url
    else:
        wxoauth = ComponentOAuth(wxclient.appid, component_appid='', component_access_token=wxclient.token,
                                 redirect_uri=url, scope='snsapi_userinfo', state=state)
        url = wxoauth.authorize_url
        logging.info(wxoauth.authorize_url)
    return wxclient.send_template_message(user_id, template_id, data, url)


def get_user_info(self, code, state='login'):
    entry = wxenv(self.env)
    wxclient = entry.wxclient
    oauth = WeChatOAuth(wxclient.appid, wxclient.appsecret, redirect_uri='', scope='snsapi_base', state=state)
    access_token = oauth.fetch_access_token(code)
    user_info = oauth.get_user_info(access_token['openid'], access_token=access_token['access_token'])
    logging.info(user_info)
    return user_info


def get_img_data(pic_url):
    import requests
    headers = {
        'Accept': 'textml,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cache-Control': 'no-cache',
        'Host': 'mmbiz.qpic.cn',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }
    r = requests.get(pic_url, headers=headers, timeout=50)
    return r.content
