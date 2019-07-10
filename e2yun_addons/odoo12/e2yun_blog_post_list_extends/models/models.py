# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import random
from odoo.modules.module import get_module_resource
from urllib.request import urlretrieve
import base64
import os

try:
    from urlextract import URLExtract
except:
    print('need install urlextract!')


class BlogPostBatch(models.TransientModel):
    _name = 'blog.post.extends.batch'

    preview_user_id = fields.Many2one('wx.user', string='预览用户')

    def blog_post_send_to_preview(self):
        if not self.preview_user_id:
            raise Exception(_('必须输入用户信息'))
        ctx = self._context.copy()
        wx_media = self.env['wx.media']

        active_model = ctx.get('active_model')
        active_ids = ctx.get('active_ids', [])

        blogs = self.env[active_model].browse(active_ids)
        server_url = self.env['ir.config_parameter'].sudo().get_param('server_url')
        articless = []
        for blog in blogs:
            thumb_media_id = False
            # wx_file_path = get_module_resource('wx_tools', 'static/wx')
            # file_image = blog.main_image
            if not blog.transfer_to_wx_flag:
                if blog.main_image:
                    img = base64.b64decode(blog.main_image)
                    file = open('./thumb.gif', 'wb')
                    file.write(img)
                    file.close()

                    thumb_media_upload = wx_media.upload_image('./thumb.gif')
                    thumb_media_id = thumb_media_upload['thumb_media_id']

                extractor = URLExtract()
                urls = extractor.find_urls(blog.content, only_unique=True)
                wx_content = blog.content
                for url in urls:
                    try:
                        urlretrieve(url, './news.jpg')
                        import imghdr
                        imgType = imghdr.what('./news.jpg')
                        if imgType:
                            news_media_upload = wx_media.upload_news_picture('./news.jpg')
                            wx_content = wx_content.replace(url, news_media_upload['url'])
                    except:
                        continue

                blog.wx_content = wx_content
                blog.thumb_media_id = thumb_media_id
                blog.transfer_to_wx_flag = True
                try:
                    os.remove('./thumb.gif')
                    os.remove('./news.jpg')
                except:
                    pass
            blog_url = server_url + blog.website_url
            articles = {
                "thumb_media_id": blog.thumb_media_id,
                "author": blog.create_uid.name,
                "title": blog.name,
                "content_source_url": blog_url,
                "content": '%s' % blog.wx_content,
                "digest": "digest",
                "show_cover_pic": 1,
                "need_open_comment": 1,
                "only_fans_can_comment": 1
            }
            articless.append(articles)

        randon_number = random.randint(100000, 999999)
        mediaid = wx_media.upload_articles(articless, '我的文章-%s' % randon_number)
        print(mediaid)

        wx_media = self.env['wx.media'].search([('media_id', '=', mediaid['media_id'])])
        preview_user_id = self.preview_user_id

        self.env['wx.send.mass'].create(
            {'wx_media_id': wx_media.id, 'preview_user_id': preview_user_id.id}).preview_send()

        return {
            'warning': {
                'title': 'Tips',
                'message': '同步成功'
            }
        }

    def blog_post_send_to_wx(self):
        # if not self.preview_user_id:
        #     raise Exception(_('必须输入用户信息'))
        ctx = self._context.copy()
        wx_media = self.env['wx.media']

        active_model = ctx.get('active_model')
        active_ids = ctx.get('active_ids', [])

        blogs = self.env[active_model].browse(active_ids)
        server_url = self.env['ir.config_parameter'].sudo().get_param('server_url')
        articless = []
        for blog in blogs:
            thumb_media_id = False
            wx_file_path = get_module_resource('e2yun_blog_post_list_extends', 'static/wx')
            # file_image = blog.main_image
            if not blog.transfer_to_wx_flag:
                if blog.main_image:
                    img = base64.b64decode(blog.main_image)
                    file = open('%s/thumb.gif' % wx_file_path, 'wb')
                    file.write(img)
                    file.close()

                    thumb_media_upload = wx_media.upload_image('%s/thumb.gif' % wx_file_path)
                    thumb_media_id = thumb_media_upload['thumb_media_id']

                extractor = URLExtract()
                urls = extractor.find_urls(blog.content, only_unique=True)
                wx_content = blog.content
                for url in urls:
                    try:
                        urlretrieve(url, '%s/news.jpg' % wx_file_path)
                        import imghdr
                        imgType = imghdr.what( '%s/news.jpg' % wx_file_path)
                        if imgType:
                            news_media_upload = wx_media.upload_news_picture( '%s/news.jpg' % wx_file_path)
                            wx_content = wx_content.replace(url, news_media_upload['url'])
                    except:
                        continue

                blog.wx_content = wx_content
                blog.thumb_media_id = thumb_media_id
                blog.transfer_to_wx_flag = True
                try:
                    os.remove( '%s/news.jpg' % wx_file_path)
                    os.remove( '%s/news.jpg' % wx_file_path)
                except:
                    pass
            blog_url = server_url + blog.website_url
            articles = {
                "thumb_media_id": blog.thumb_media_id,
                "author": blog.create_uid.name,
                "title": blog.name,
                "content_source_url": blog_url,
                "content": '%s' % blog.wx_content,
                "digest": "digest",
                "show_cover_pic": 1,
                "need_open_comment": 1,
                "only_fans_can_comment": 1
            }
            articless.append(articles)

        randon_number = random.randint(100000, 999999)
        mediaid = wx_media.upload_articles(articless, '我的文章-%s' % randon_number)
        print(mediaid)

        wx_media = self.env['wx.media'].search([('media_id', '=', mediaid['media_id'])])
        preview_user_id = self.preview_user_id

        self.env['wx.send.mass'].create(
            {'wx_media_id': wx_media.id, 'preview_user_id': preview_user_id.id}).preview_send()

        return {
            'warning': {
                'title': 'Tips',
                'message': '同步成功'
            }
        }
