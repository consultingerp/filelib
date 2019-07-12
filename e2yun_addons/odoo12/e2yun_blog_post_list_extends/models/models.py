# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import random
from odoo.modules.module import get_module_resource
from urllib.request import urlretrieve
import base64
import os
from PIL import Image

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
            wx_file_path = get_module_resource('e2yun_blog_post_list_extends', 'static/wx')
            # file_image = blog.main_image
            if not blog.transfer_to_wx_flag:
                if blog.cover_properties:
                    cover_properties = eval(blog.cover_properties)
                    if 'background-image' in eval(blog.cover_properties):
                        imageurl = cover_properties['background-image'].replace('url(', '').replace(')', '')
                        if 'http' not in imageurl:
                            # imageurl = server_url + imageurl

                            attench_id = imageurl.replace('/web/image/', '')[
                                         0: imageurl.replace('/web/image/', '').index('/')]

                            datas = self.env['ir.attachment'].browse(int(attench_id)).datas

                            img = base64.b64decode(datas)
                            file = open('%s/thumb.jpg' % wx_file_path, 'wb')
                            file.write(img)
                            file.close()

                        else:
                            urlretrieve(imageurl, '%s/thumb.jpg' % wx_file_path)
                        quality = 80
                        step = 5
                        while os.path.getsize('%s/thumb.jpg' % wx_file_path) / 1024 > 64:
                            file_path = '%s/thumb.jpg' % wx_file_path
                            im = Image.open(file_path)
                            # 获得图像尺寸:
                            # w, h = im.size
                            # 缩放到50%:
                            # im.resize((int(w / 0.8), int(h / 0.8)), Image.ANTIALIAS)
                            # 把缩放后的图像用jpeg格式保存:
                            if im.mode == "P":
                                im = im.convert('RGB')
                            im.save(file_path, 'JPEG', quality=quality)
                            if quality - step < 0:
                                break
                            quality -= step
                    else:
                        raise Exception(_('必须要有封面图片，请在文章编辑中输入！'))

                    # img = base64.b64decode(blog.main_image)
                    # file = open('%s/thumb.gif' % wx_file_path, 'wb')
                    # file.write(img)
                    # file.close()

                    thumb_media_upload = wx_media.upload_image('%s/thumb.jpg' % wx_file_path)
                    thumb_media_id = thumb_media_upload['thumb_media_id']
                else:
                    raise Exception(_('必须要有封面图片，请在文章编辑中填入！'))
                extractor = URLExtract()
                urls = extractor.find_urls(blog.content, only_unique=True)
                wx_content = blog.content
                for url in urls:
                    try:
                        urlretrieve(url, '%s/news.jpg' % wx_file_path)
                        import imghdr
                        imgType = imghdr.what('%s/news.jpg' % wx_file_path)
                        if imgType:
                            news_media_upload = wx_media.upload_news_picture('%s/news.jpg' % wx_file_path)
                            wx_content = wx_content.replace(url, news_media_upload['url'])
                    except:
                        continue

                blog.wx_content = wx_content
                blog.thumb_media_id = thumb_media_id
                blog.transfer_to_wx_flag = True
                try:
                    os.remove('%s/thumb.jpg' % wx_file_path)
                    os.remove('%s/news.jpg' % wx_file_path)
                except:
                    pass
            blog_url = server_url + blog.website_url
            articles = {
                "thumb_media_id": blog.thumb_media_id,
                "author": blog.create_uid.name,
                "title": blog.name,
                "content_source_url": blog_url,
                "content": '%s' % blog.wx_content,
                "digest": blog.subtitle,
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

    def get_size(file):
        # 获取文件大小:KB
        size = os.path.getsize(file)
        return size / 1024

    def get_outfile(infile, outfile):
        if outfile:
            return outfile
        dir, suffix = os.path.splitext(infile)
        outfile = '{}-out{}'.format(dir, suffix)
        return outfile

    def compress_image(infile, outfile='', mb=150, step=10, quality=80):
        """不改变图片尺寸压缩到指定大小
        :param infile: 压缩源文件
        :param outfile: 压缩文件保存地址
        :param mb: 压缩目标，KB
        :param step: 每次调整的压缩比率
        :param quality: 初始压缩比率
        :return: 压缩文件地址，压缩文件大小
        """
        o_size = get_size(infile)
        if o_size <= mb:
            return infile
        outfile = get_outfile(infile, outfile)
        while o_size > mb:
            im = Image.open(infile)
            im.save(outfile, quality=quality)
            if quality - step < 0:
                break
            quality -= step
            o_size = get_size(outfile)
        return outfile, get_size(outfile)
