# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class StockDeliveryController(http.Controller):

    @http.route(['/deliveryBarcode/web/'], type='http', auth='user')
    def b(self, debug=False, **k):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/deliveryBarcode/web')

        return request.render('srm_stock_delivery.delivery_barcode_index')

