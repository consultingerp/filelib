# -*- coding: utf-8 -*-
from odoo import http
import base64
from odoo.http import request

class AgreementDownloadDoc(http.Controller):

    @http.route('/e2yun/agreement/download/doc/<string:id>',  type='http', auth="public")
    def download(self,id):
        print(id)

    @http.route([
        "/agreement/wordEdit/<int:agreement_id>"
    ], type='http', auth="public")
    def wordEdit(self,agreement_id):
        #order = request.env['purchase.order'].sudo().browse(order_id)
        clause = request.env['agreement.clause']  # 条款
        clauseListData = clause.search([('agreement_id', '=', agreement_id)])


        values = {
            'agreement_id':agreement_id,
            'content': clauseListData[0].content,
        }

        return request.render('e2yun_agreement_docx_import.qweb_agreement_word_edit', values)

    @http.route(['/agreement/wordSubmit/<int:agreement_id>'], type='http', auth="public")
    def wordSubmit(self, agreement_id, **post):
        print(agreement_id)