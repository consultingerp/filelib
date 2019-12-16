# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import re
import difflib
class Agreement(models.Model):  #合同
    _inherit = "agreement"

    # def create(self, vals_list):
    #     print(vals_list)
    #     return super(Agreement,self).create(vals_list)

    def wordEdit(self):

        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'new',
        #     'url': '/agreement/wordEdit/5',
        # }
        print(111)
        agreement_word_data = self.env['agreement.word.data']  # wordData

        clauseListData = agreement_word_data.search(
            [('agreement_id', '=', self.id), ('detail', '=', True)])


        return {
            'type': 'ir.actions.act_window',
            'res_model':'agreement.word.data',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': clauseListData[0].id,
            'context': dict(self._context),
        }

class AgreementWordData(models.Model):  #条款
    _name = "agreement.word.data"
    master_word_id = fields.Integer('Master Word Id')
    the_editor = fields.Boolean('The Editor')
    sequence = fields.Integer(string="Sequence")
    agreement_id = fields.Integer()
    content = fields.Html(string="Clause Content")
    old_text=fields.Html()
    new_text = fields.Html()
    detail=fields.Boolean()
    edit_type=fields.Char()
    alignment=fields.Char()
    font_Name=fields.Char()
    font_size=fields.Char()

    def write(self, vals_list):
        content_old=self.content
        oldStr = re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", content_old)
        content_new=vals_list['content']
        newStr = re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", content_new)
        if oldStr != newStr:
            opcodes = difflib.SequenceMatcher(None, oldStr, newStr).get_opcodes()
            for op, af, at, bf, bt in opcodes:
                if op == 'delete':
                    oldStr = oldStr[af:at]
                    newStr = newStr[bf:bt]
                    refind1 = re.findall(r"id(.+?)" + str(newStr) + "", content_new)
                    if refind1 and refind1[0]:
                        refind2 = re.findall(r"=(.+?) ", refind1[0])  #
                        if refind2 and refind2[0]:
                            sql = "update agreement_word_data set edit_type=%s ,old_text=%s, new_text=%s ,the_editor=True where agreement_id=%s and detail=False and sequence=%s"
                            self.env.cr.execute(sql, ('replace', oldStr, newStr, self.agreement_id, refind2[0].replace('"', '')))
                elif op == 'replace' and (oldStr[af:at] and newStr[bf:bt]):
                    oldStr = oldStr[af:at]
                    newStr = newStr[bf:bt]
                    refind1 = re.findall(r"id(.+?)" + str(newStr) + "", content_new)
                    if refind1 and refind1[0]:
                        refind2 = re.findall(r"=(.+?) ", refind1[0])  #
                        if refind2 and refind2[0]:
                            sql="update agreement_word_data set edit_type=%s ,old_text=%s, new_text=%s,the_editor=True where agreement_id=%s and detail=False and sequence=%s"
                            self.env.cr.execute(sql, ('replace',oldStr,newStr,self.agreement_id,refind2[0].replace('"', '')))
                elif op == 'insert':
                    oldStr = oldStr[af:at]
                    newStr = newStr[bf:bt]
                    refind1 = re.findall(r"id(.+?)" + str(newStr) + "", content_new)
                    if refind1 and refind1[0]:
                        refind2 = re.findall(r"=(.+?) ", refind1[0])  #
                        if refind2 and refind2[0]:
                            sql = "update agreement_word_data set edit_type=%s ,old_text=%s, new_text=%s ,the_editor=True where agreement_id=%s and detail=False and sequence=%s"
                            self.env.cr.execute(sql, ('replace', oldStr, newStr, self.agreement_id, refind2[0].replace('"', '')))

        #< del > ¥4000 < / del >

        #vals_list['the_editor']=True

        agreement_word_data = self.env['agreement.word.data']  # wordData
        clauseListData = agreement_word_data.search([('agreement_id', '=',  self.agreement_id),('detail','=',False)])
        allContent=""
        content=""
        for clauseObj in clauseListData:
          if  clauseObj.content or clauseObj.content!="":
            text = re.findall(r'[^\*"<p></p>]', clauseObj.content, re.S)
            text = "".join(text)
            font_size=float(clauseObj.font_size)+2
            if clauseObj.alignment=='1':
                p = "<p id=" + str(clauseObj.sequence) + " style = 'text-align:center; font-size: " + str(font_size) + "px;'>"
            elif clauseObj.alignment=='2':
                p = "<p id=" + str(clauseObj.sequence) + " style = 'text-align:right; font-size: " + str(font_size)  + "px;'>"
            else:
                p = "<p id=" + str(clauseObj.sequence) + " style ='font-size: " + str(font_size)  + "px;'>"
            if clauseObj.the_editor==True:

                content = p + text + "" \
                                     "<del style='color: rgb(255, 0, 0);font-size: " + str(font_size) + "px;'>"+str(clauseObj.old_text)+"</del>" \
                                                                                                    "<font style='color: rgb(255, 0, 0);font-size: " + str(font_size)  + "px;'>" + str(clauseObj.new_text) + "</font></p>"

            else:
                content = p + text+"</p>"
          else:
            content = "<br/>"
          allContent = allContent + content
        vals_list['content']=allContent
        return super(AgreementWordData,self).write(vals_list)











