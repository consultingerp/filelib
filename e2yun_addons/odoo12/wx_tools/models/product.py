# -*-coding:utf-8-*-
import base64
import os

import qrcode
from PIL import Image

from odoo import fields, models, tools
from odoo.modules.module import get_module_resource
from ..controllers import client
import requests


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    qrcode = fields.Char(u'二维码')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    def _get_qrcodeimg(self):
        entry = client.wxenv(self.env)
        if not self.qrcode:
            wx_file_path = get_module_resource('wx_tools', 'static/wx')
            file_name = 'product%s.png' % self.id
            url = entry.server_url + "/shop/product/%s" % self.id
            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=5,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            # 生成图片
            img = qr.make_image(fill_color="#FFFFFF",back_color="#000000")
            product_name = 'product_%s.jpeg' % self.id
            product_image = os.path.join(wx_file_path, product_name)
            # _data = client.get_img_data(
            #     '%s/web/image?model=product.template&id=%s&field=image_medium' % (entry.server_url, self.id))
            # with open(product_image, 'wb') as str2datas:
            #     str2datas.write(_data)
            img_product = requests.get('%s/web/image?model=product.template&id=%s&field=image' % (entry.server_url, self.id))
            product_file = open(product_image, 'ab')  # 存储图片，多媒体文件需要参数b（二进制文件）
            product_file.write(img_product.content)  # 多媒体存储content
            product_file.close()
            icon = Image.open(product_image)
            # 获取图片的宽高
            img_w, img_h = img.size
            # 参数设置logo的大小
            factor = 6
            size_w = int(img_w / factor)
            size_h = int(img_h / factor)
            icon_w, icon_h = icon.size
            if icon_w > size_w:
                icon_w = size_w
            if icon_h > size_h:
                icon_h = size_h
            # 重新设置logo的尺寸
            icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
            # 得到画图的x，y坐标，居中显示
            w = int((img_w - icon_w) / 2)
            h = int((img_h - icon_h) / 2)
            # logo照
            img.paste(icon, (w, h), mask=None)

            # img = qrcode.make(url)
            qrcodeimg_pic = os.path.join(wx_file_path, file_name)
            with open(qrcodeimg_pic, 'wb') as product_file:
                img.save(product_file)
            self.write({'qrcode': file_name})
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % file_name

        else:
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % self.qrcode
