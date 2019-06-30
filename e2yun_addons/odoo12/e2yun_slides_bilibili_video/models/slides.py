# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from urllib import request, error, parse
import base64
import requests
from odoo import api, fields, models, SUPERUSER_ID, _


class Slide(models.Model):
    _inherit = 'slide.slide'

    def _get_embed_code(self):
        super(Slide, self)._get_embed_code()

        for record in self:
            if record.slide_type == 'video':
                if record.document_id and record.mime_type == "bilibili":
                    record.embed_code = """
                        <iframe frameborder="0" width="640" height="498"
                            src="http://player.bilibili.com/player.html?aid=%s&cid=%s&page=%s" 
                            scrolling="no" border="0" frameborder="no" framespacing="0" 
                            allowfullscreen="true"></iframe>
                    """ % (record.document_id.split(':')[0],
                           record.document_id.split(':')[1],
                           record.document_id.split(':')[2])

                    # for qq vedio

    def _fetch_bilibili_data(self, base_url, data, content_type=False):
        result = {'values': dict()}
        try:
            if content_type == 'json':
                if data:
                    base_url = base_url + '%s' % parse.urlencode(data)
                req = request.Request(base_url)
                content = str(request.urlopen(req).read(), encoding="utf-8")
                result['values'] = eval(content.replace('false','0').replace('true','1'))

                if result['values'].get('code') != 0:
                    result['error'] = result['values'].get('message')
            elif content_type == 'image':
                response = requests.get(base_url, params=data)
                response.raise_for_status()
                result['values'] = base64.b64encode(response.content)
                # req = request.Request(base_url)
                # content = request.urlopen(req).read()
                #
                # result['values'] = base64.b64encode(content)
            else:
                result['values'] = ""
        except error.HTTPError as e:
            result['error'] = e.read()
            e.close()
        except error.URLError as e:
            result['error'] = e.reason
        return result

    def _find_document_data_from_url(self, url):
        # bilibili video
        #expr = re.compile(r'^.*((youtu.be/)|(v/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*')
        #*.*(youku.com\ / ).*(sharev)\??vid =?([ ^  # \&\?]*).*
        expr = re.compile(r'.*?(bilibili.com).*\??aid=(\d+).*cid=(\d+).*page=(\d+)')
        arg = expr.match(url)
        document_id = arg and arg.group(2)+':'+ arg.group(3)+':'+ arg.group(4)
        if document_id:
            return ('bilibili', document_id)

        return super(Slide, self)._find_document_data_from_url(url)

    def _parse_bilibili_video_title(self, res):
        title = ""

        try:
            title = res['values']['data']['title']
        except:
            title = ""

        return title

    def _parse_bilibili_video_thumbnails(self, res):
        img_url = ""

        try:
            img_url = res['values']['data']['pic'].replace("\\",'')
        except:
            img_url = ""

        return img_url

    def _parse_bilibili_video_description(self, res):
        img_url = ""

        try:
            description = res['values']['data']['desc']
        except:
            description = ""

        return description

    def _parse_bilibili_document(self, document_id, only_preview_fields):
        fetch_res = self._fetch_bilibili_data(
            'https://api.bilibili.com/x/web-interface/view?', {
                                              'aid': document_id.split(':')[0],
                                              }, 'json'
        )

        if fetch_res.get('error'):
            return fetch_res

        title = self._parse_bilibili_video_title(fetch_res)
        img_url = self._parse_bilibili_video_thumbnails(fetch_res)
        description = self._parse_bilibili_video_description(fetch_res)
        values = {'slide_type': 'video', 'document_id': document_id}

        if only_preview_fields:
            values.update({
                'url_src': img_url,
                'title': title,
                'description': description,
            })

            return values

        values.update({
            'name': title,
            'image': self._fetch_bilibili_data(img_url, {}, 'image')['values'],
            'mime_type': "bilibili",
            'description': description,
        })
        return {'values': values}