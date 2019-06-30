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
                if record.document_id and record.mime_type == "youku":
                    record.embed_code = """
                        <iframe frameborder="0" width="640" height="498"
                            src="http://player.youku.com/embed/%s" frameborder=0
                            allowfullscreen></iframe>
                    """ % (record.document_id)

                    # for qq vedio

    def _fetch_youku_data(self, base_url, data, content_type=False):
        result = {'values': dict()}
        try:
            if content_type == 'json':
                if data:
                    base_url = base_url + '%s' % parse.urlencode(data)
                req = request.Request(base_url)
                content = str(request.urlopen(req).read(), encoding="utf-8")
                result['values'] = eval(content)

                if result['values'].get('error'):
                    result['error'] = result['values'].get('error')
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
        # youku video
        #expr = re.compile(r'^.*((youtu.be/)|(v/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*')
        #*.*(youku.com\ / ).*(sharev)\??vid =?([ ^  # \&\?]*).*
        expr = re.compile(r'.*(youku.com).*(embed\/)([^#\&\?]*).*')
        arg = expr.match(url)
        document_id = arg and arg.group(3) or False
        if document_id:
            return ('youku', document_id)

        return super(Slide, self)._find_document_data_from_url(url)

    def _parse_youku_video_title(self, res):
        title = ""

        try:
            title = res['values']['title']
        except:
            title = ""

        return title

    def _parse_youku_video_thumbnails(self, res):
        img_url = ""

        try:
            img_url = res['values']['thumbnail'].replace("\\",'')
        except:
            img_url = ""

        return img_url

    def _parse_youku_video_description(self, res):
        img_url = ""

        try:
            description = res['values']['description']
        except:
            description = ""

        return description

    def _parse_youku_document(self, document_id, only_preview_fields):
        fetch_res = self._fetch_youku_data(
            'https://api.youku.com/videos/show.json?', {'client_id': "0edbfd2e4fc91b72",'video_id': document_id}, 'json'
        )

        if fetch_res.get('error'):
            return fetch_res

        title = self._parse_youku_video_title(fetch_res)
        img_url = self._parse_youku_video_thumbnails(fetch_res)
        description =self._parse_youku_video_description(fetch_res)
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
            'image': self._fetch_youku_data(img_url, {}, 'image')['values'],
            'mime_type': "youku",
            'description': description,
        })
        return {'values': values}