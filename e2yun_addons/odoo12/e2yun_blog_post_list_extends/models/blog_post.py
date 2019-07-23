# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


class BlogPostBatch(models.Model):
    _inherit = 'blog.post'

    _order = 'good_count desc,visits desc'

    main_image = fields.Binary("封面图片", attachment=True)
    thumb_media_id = fields.Char("微信封面图片media_id")
    wx_content = fields.Html('微信文章内容')
    transfer_to_wx_flag = fields.Boolean('已经转微信')
    good_count = fields.Integer('感兴趣数',default=0)

    @api.model
    def click_good(self):
        ctx = self._context.copy()
        blog_id = ctx.get('blog_id',False)
        if blog_id:
            blog = self.browse(int(blog_id))
            blog.good_count = blog.good_count + 1


