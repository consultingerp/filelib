# -*- coding: utf-8 -*-
from odoo import http
import base64
from odoo.http import request
import re
import difflib
from datetime import datetime, timedelta
class AgreementDownloadDoc(http.Controller):

    @http.route('/e2yun/agreement/download/doc/<string:id>',  type='http', auth="public")
    def download(self,id):
        print(id)

    @http.route([
        "/agreement/wordEdit/<int:agreement_id>",
        "/agreement/wordEdit/<int:agreement_id>/<string:debug>"
    ], type='http', auth="public")
    def wordEdit(self,agreement_id,debug):
        #order = request.env['purchase.order'].sudo().browse(order_id)

        agreement_word_data = request.env['agreement.word.data']  # wordData

        clauseListData = agreement_word_data.search(
            [('agreement_id', '=', agreement_id), ('detail', '=', False)])
        values = {
            'agreement_id':agreement_id,
            'content': clauseListData,
        }

        return request.render('e2yun_agreement_docx_import.qweb_agreement_word_edit', values)

    @http.route(['/agreement/wordSubmit/<int:agreement_id>'], type='http', auth="public")
    def wordSubmit(self, agreement_id, **post):
        if True:
            content_id=post["content_id"]
            content_old = post["content_old"]
            content_new = post["content"]
            oldStr = re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", content_old)
            newStr = re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", content_new)
            if oldStr != newStr:
                agreement_word_data = request.env['agreement.word.data']  # wordData
                opcodes = difflib.SequenceMatcher(None, oldStr, newStr).get_opcodes()
                for op, af, at, bf, bt in opcodes:
                    if op == 'delete':
                        oldStr = oldStr[af:at]
                        newStr = newStr[bf:bt]
                        clauseListData = agreement_word_data.search(
                            [('id', '=', content_id)])
                        up_val = {}
                        up_val['edit_type'] = "delete"
                        up_val['old_text'] = ""
                        up_val['new_text'] = content_new
                        up_val['the_editor'] = True
                        clauseListData[0].write(up_val)

                    elif op == 'replace' and (oldStr[af:at] and newStr[bf:bt]):
                        oldStr = oldStr[af:at]
                        newStr = newStr[bf:bt]
                        clauseListData = agreement_word_data.search(
                                        [('id', '=', content_id)])
                        up_val = {}
                        up_val['edit_type'] = "replace"
                        up_val['old_text'] = oldStr
                        up_val['new_text'] = newStr
                        up_val['the_editor'] = True
                        clauseListData[0].write(up_val)

                    elif op == 'insert':
                        oldStr = oldStr[af:at]
                        newStr = newStr[bf:bt]
                        clauseListData = agreement_word_data.search(
                            [('id', '=', content_id)])
                        up_val = {}
                        up_val['edit_type'] = "insert"
                        up_val['old_text'] = ""
                        up_val['new_text'] = content_new
                        up_val['the_editor'] = True
                        clauseListData[0].write(up_val)


        agreement_word_data = request.env['agreement.word.data']  # wordData
        clauseListData = agreement_word_data.search(
            [('agreement_id', '=', agreement_id), ('detail', '=', False)])
        values = {
            'agreement_id': agreement_id,
            'content': clauseListData,
        }
        agreementObj = request.env['agreement'].search(
                            [('id', '=', agreement_id)])
        agreementVal={}
        agreementVal['write_date']=datetime.now()

        agreementObj[0].write(up_val)


        return request.render('e2yun_agreement_docx_import.qweb_agreement_word_edit', values)


    @http.route([
        "/agreement/preview/<int:agreement_id>",
        "/agreement/preview/<int:agreement_id>/<string:debug>"
    ], type='http', auth="public")
    def preview(self,agreement_id,debug):
      print(agreement_id)
      agreement_obj = request.env['agreement']
      docs = agreement_obj.search(
            [('id', '=', agreement_id)])
      values = {
         'docs':docs,
      }
      return request.render('e2yun_agreement_docx_import.qweb_agreement_word_preview', values)