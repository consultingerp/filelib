# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class BlogPostBatch(models.Model):
    _inherit = 'blog.post'

    main_image = fields.Binary("封面图片", attachment=True)
    thumb_media_id = fields.Char("微信封面图片media_id")
    wx_content = fields.Html('微信文章内容')
    transfer_to_wx_flag = fields.Boolean('已经转微信')

