# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy.client.api.base import BaseWeChatAPI


class WeChatMedia(BaseWeChatAPI):

    def upload_articles(self, articles):
        """
        上传图文消息素材
        详情请参考
        http://mp.weixin.qq.com/wiki/15/5380a4e6f02f2ffdc7981a8ed7a40753.html

        :param articles: 图文消息数组
        :return: 返回的 JSON 数据包
        """
        articles_data = []
        for article in articles:
            articles_data.append({
                'thumb_media_id': article['thumb_media_id'],
                'title': article['title'],
                'content': article['content'],
                'author': article.get('author', ''),
                'content_source_url': article.get('content_source_url', ''),
                'digest': article.get('digest', ''),
                'show_cover_pic': article.get('show_cover_pic', 0)
            })
        return self._post(
            'media/uploadnews',
            data={
                'articles': articles_data
            }
        )

    def upload_mass_image(self, media_file):
        """
        上传群发消息内的图片
        详情请参考
        http://mp.weixin.qq.com/wiki/15/5380a4e6f02f2ffdc7981a8ed7a40753.html

        :param media_file: 要上传的文件，一个 File-object
        :return: 上传成功时返回图片 URL
        """
        res = self._post(
            url='https://api.weixin.qq.com/cgi-bin/media/uploadimg',
            files={
                'media': media_file
            },
            result_processor=lambda x: x['url']
        )
        return res
