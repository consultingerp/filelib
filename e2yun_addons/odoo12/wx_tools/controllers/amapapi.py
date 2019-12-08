# -*-coding:utf-8-*-

import requests

from odoo.exceptions import UserError


def geocodegeo(self, address, city=''):
    # 根据地址获取位置坐标
    amapkey = self.env['ir.config_parameter'].sudo().get_param('amapkey')
    mapurl = 'https://restapi.amap.com/v3/geocode/geo?key=%s&address=%s&city=%s' % (amapkey, address, city)
    try:
        result = requests.get(mapurl).json()
    except Exception as e:
        raise UserError('获取地址失败%s' % e)
    if result['status'] == 0:
        raise UserError('获取地址失败')
    try:
        geo = result['geocodes'][0]['location']
        return geo
    except (KeyError, ValueError, IndexError):
        return '0.0,0.0'
        # raise UserError('用户址转换出错:%s' % address)


def geocoderegeo(self, location):
    # 根据坐标获取位置
    amapkey = self.env['ir.config_parameter'].sudo().get_param('amapkey')
    mapurl = 'https://restapi.amap.com/v3/geocode/regeo?key=%s&location=%s&poitype=&radius=1000' \
             '&extensions=all&batch=false&roadlevel=0' % (amapkey, location)
    try:
        result = requests.get(mapurl).json()
    except Exception as e:
        raise UserError('获取地址失败%s' % e)
    if result['status'] == 0:
        raise UserError('获取地址失败')
    try:
        #geo = result['regeocode']['formatted_address']
        geo = result['regeocode']
        return geo
    except (KeyError, ValueError):
        return None


def coordinateconvert(self, location):
    # 微信地址转换
    amapkey = self.env['ir.config_parameter'].sudo().get_param('amapkey')
    mapurl = 'https://restapi.amap.com/v3/assistant/coordinate/convert?key=%s&locations=%s&coordsys=gps' \
             % (amapkey, location)
    try:
        result = requests.get(mapurl).json()
    except Exception as e:
        raise UserError('获取地址失败%s' % e)
    if result['status'] == 0:
        raise UserError('获取地址失败')
    try:
        geo = result['locations']
        return geo
    except (KeyError, ValueError):
        return None


def amapdistance(self, origins, destination):
    # 位置计算 车的位置
    amapkey = self.env['ir.config_parameter'].sudo().get_param('amapkey')
    mapurl = 'stapi.amap.com/v3/distance?key=您的key&origins=%s&destination=%s&type=1' \
             % (amapkey, origins, destination)
    try:
        result = requests.get(mapurl).json()
    except Exception as e:
        raise UserError('获取地址失败%s' % e)
    if result['status'] == 0:
        raise UserError('获取地址失败')
    try:
        return result
    except (KeyError, ValueError):
        return None
