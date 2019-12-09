# -*- coding: utf-8 -*-
from odoo import http
import base64


class AgreementDownloadDoc(http.Controller):

    @http.route('/e2yun/agreement/download/doc/<string:id>',  type='http', auth="public")
    def download(self,id):
        print(id)



