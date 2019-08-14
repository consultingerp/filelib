# -*-coding:utf-8-*-
from odoo import api, fields, models, _
import qrcode
from ..controllers import client
from odoo.modules.module import get_module_resource
import os


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
            img = qrcode.make(url)
            qrcodeimg_pic = os.path.join(wx_file_path, file_name)
            with open(qrcodeimg_pic, 'wb') as f:
                img.save(f)
            self.write({'qrcode': file_name})
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % file_name

        else:
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % self.qrcode
