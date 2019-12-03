# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
import datetime
import logging

from odoo import http

_logger = logging.getLogger(__name__)


class WxSaleOrder(http.Controller):
    @http.route('/website/saleorder', type='http', auth="public", website=True)
    def saleorder(self, **kwargs):
        url_ = request.httprequest.url
        _logger.info("参数打印:%s" % url_)
        return request.render("wx_sale_order.order_test", {'jsapi_ticket': request.env.user.get_jsapi_ticket(url_)})
