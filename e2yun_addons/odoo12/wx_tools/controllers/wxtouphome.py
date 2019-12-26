# -*-coding:utf-8-*-

import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug import urls

from odoo import api
from odoo import http
from odoo.http import request
from odoo.tools import pycompat


class WXToUpHome(http.Controller):

    @http.route(['/touphome'], type='http', auth="public")
    def touphome(self, **kwargs):
        url = request.env['ir.config_parameter'].sudo().get_param('uphome_url')
        function = request.env.user.function
        if function:
            ss_type = 'T'
            url = url + "/service/service"
        else:
            ss_type = 'C'
            url = url + "/service/order_list"
        if request.env.user.wx_user_id:
            ss_wx_code = request.env.user.wx_user_id.openid
        else:
            ss_wx_code = ""
        return self.redirect_with_hash(url, ss_wx_code, ss_type)

    @api.model
    def redirect_with_hash(self, url, ss_wx_code, ss_type, code=303):
        # Most IE and Safari versions decided not to preserve location.hash upon
        # redirect. And even if IE10 pretends to support it, it still fails
        # inexplicably in case of multiple redirects (and we do have some).
        # See extensive test page at http://greenbytes.de/tech/tc/httpredirects/
        if request.httprequest.user_agent.browser in ('firefox',):
            return werkzeug.utils.redirect(url, code)
        # FIXME: decide whether urls should be bytes or text, apparently
        # addons/website/controllers/main.py:91 calls this with a bytes url
        # but addons/web/controllers/main.py:481 uses text... (blows up on login)
        url = pycompat.to_text(url).strip()
        if urls.url_parse(url, scheme='http').scheme not in ('http', 'https'):
            url = u'http://' + url
        url = url.replace("'", "%27").replace("<", "%3C")
        return "<html><head>" \
               "<body>" \
               "<form  id='form1' name='form1' action='%s' method='post'> " \
               "<input type=hidden id='ss_wx_code' name='ss_wx_code' value='%s'> " \
               "<input type=hidden id='ss_type' name='ss_type' value='%s'>" \
               "<script>var form = document.getElementById('form1'); form.submit();</script>" \
               "</body></head></html>" % (url, ss_wx_code, ss_type)
