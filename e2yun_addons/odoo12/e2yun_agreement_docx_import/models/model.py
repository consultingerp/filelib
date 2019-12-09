# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import sys
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from docx.shared import RGBColor
from docx import Document
from docx.shared import Pt,Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

class DocxImport(models.TransientModel):
    _name = "agreement.docx.import"
    _description = "agreement docx Import"

    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict', required=True)
    name = fields.Char('file path')
    data = fields.Binary('File')
    filename = fields.Char('File Name')

    @api.multi
    def import_docx(self):
        this = self[0]
        full_path = this.name
        doc = Document(full_path)

        recital = self.env['agreement.recital']    #叙述
        clause = self.env['agreement.clause']      #条款
        section = self.env['agreement.section']    #章节
        appendix = self.env['agreement.appendix']  #附录

        vals=[]
       # 每一段的内容
        i=0
        for para in doc.paragraphs:
            print(i)
            val = {}
            val['no'] =i
            val['text']=para.text
            val['style_font'] = para.style.font.name
            val['style_name'] = para.style.name
            val['style'] = para.style
            val['font'] = para.style.font
            vals.append(val)
            i=i+1


        # 每一段的编号、内容
        #for i in range(len(doc.paragraphs)):
        #    print(str(i), doc.paragraphs[i].text)
        document = Document() # 初始化文档
        for val in vals:
            print(val)
            if val['style_name'] and val['style_name']=='文档标题':
                d_title = document.add_heading(val['text'], 0)
                d_title.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                d_title.style=val['style']
                d_title.style.font.size=28
                d_title.bold = True

            else:
              p=document.add_paragraph(val['text'])
              p.style=val['style']

        #document.save('D:\\demo1203.docx')

        return True



class AgreementDownloadDoc(models.Model):
    _name = "agreement.download.doc"

    file_path = fields.Char('File Path')

    def chg_font(self,obj, fontname='微软雅黑', size=None):
         ## 设置字体函数
        obj.font.name = fontname
        #obj._element.rPr.rFonts.set(qn('w:eastAsia'), fontname)
        if size and isinstance(size, Pt):
          obj.font.size = size

    def add_text_default(self,document,text,bold,size,sytle_name,font_name):
        p = document.add_paragraph()
        r = p.add_run(text)
        r.bold = bold
        r.style.font.size = size
        r.style.name =sytle_name
        r.style.font.name=font_name

    def download_doc(self):

        path = sys.path[0]+"\\"

        agreement_id=self._context['active_id']

        attachment = self.env['ir.attachment'] # 附件

        agreement = self.env['agreement']

        agreementData = agreement.browse(agreement_id)

        recital = self.env['agreement.recital'] #叙述
        recitalListData = recital.search([('agreement_id', '=', agreement_id)])

        section = self.env['agreement.section'] #章节
        sectionListData = section.search([('agreement_id', '=', agreement_id)])

        clause = self.env['agreement.clause']  #条款
        clauseListData = clause.search([('agreement_id', '=', agreement_id)])

        appendix = self.env['agreement.appendix']  #附录
        appendixListData = appendix.search([('agreement_id', '=', agreement_id)])

        document = Document()  # 初始化文档

        for recitalObj in recitalListData:  #叙述
            if not recitalObj.doc_text:
                document.add_paragraph("")
                if recitalObj.sequence == 16:
                    #翻页
                    document.add_page_break()
                continue

            text = re.findall(r'[^\*"<p></p>]', recitalObj.content, re.S)
            text = "".join(text)
            if recitalObj.sequence==6:
                #标题
                p=document.add_heading("",0)
                r=p.add_run(text)
                p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                p.style.font.color.rgb = None
                r.style.name = recitalObj.doc_style
                r.font.size = Pt(28)
                r.bold=True
                if recitalObj.doc_font:
                    r.style.font.name=recitalObj.doc_font

            elif recitalObj.sequence==0:
                #第一行
                p = document.add_paragraph()
                r = p.add_run(text)
                p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                r.style.name = recitalObj.doc_style
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font
                r.bold = True

            elif recitalObj.sequence == 11:
                p = document.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                r=p.add_run(agreementData.partner_id.name)
                r.style.name = recitalObj.doc_style
                r.font.size=Pt(18)
                r.bold = True
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font
                #p.style.font.size=Pt(28)
                #p.style.font.color.rgb = RGBColor(0x42, 0x24, 0xE9)


            elif recitalObj.sequence == 12:
                p = document.add_paragraph()
                r=p.add_run(text)
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                r.font.size = Pt(18)
                r.bold = True
                r.style.name = recitalObj.doc_style
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font

            elif recitalObj.sequence == 13:
                p = document.add_paragraph()
                r=p.add_run(agreementData.company_id.name)
                r.font.size = Pt(18)
                r.bold = True
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                r.style.name = recitalObj.doc_style
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font

            elif recitalObj.sequence == 14:
                p = document.add_paragraph()
                r=p.add_run(text)
                r.font.size = Pt(18)
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                r.style.name = recitalObj.doc_style
                r.bold = True
                if recitalObj.doc_font:
                    p.style.font.name = recitalObj.doc_font

            elif recitalObj.sequence == 17:
                p = document.add_paragraph()
                r = p.add_run(text)
                r.style.name = recitalObj.doc_style
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font

                self.add_text_default(document, "甲方：", True, 11, '宋体', '宋体')
                document.add_paragraph()

                self.add_text_default(document, "法定代表人：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "地址：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "邮编：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "电话：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "传真：", True, 11, '宋体', '宋体')
                document.add_paragraph()
                document.add_paragraph()

                self.add_text_default(document, "乙方：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "法定代表人：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "地址：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "邮编：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "电话：", True, 11, '宋体', '宋体')
                self.add_text_default(document, "传真：", True, 11, '宋体', '宋体')

            else:
                p = document.add_paragraph()
                r=p.add_run(text)
                r.style.name = recitalObj.doc_style
                if recitalObj.doc_font:
                    r.style.font.name = recitalObj.doc_font


        for sectionObj in sectionListData:  #章节
             if not sectionObj.doc_text:
                continue
             text = re.findall(r'[^\*"<p></p>]', sectionObj.content, re.S)
             text = "".join(text)
             p = document.add_paragraph()
             r=p.add_run(sectionObj.title+".   "+text)
             r.style.name = sectionObj.doc_style
             r.style.name = '宋体'
             r.style.font.size = 11
             if sectionObj.doc_font:
                 r.style.font.name = sectionObj.doc_font
             for clauseObj in clauseListData:  # 条款
                if not clauseObj.doc_text:
                    continue
                text = re.findall(r'[^\*"<p></p>]', clauseObj.content, re.S)
                text = "".join(text)
                if clauseObj.section_id.id==sectionObj.id:
                    p = document.add_paragraph()
                    r=p.add_run(clauseObj.title+"   "+text)
                    paragraph_format = p.paragraph_format
                    paragraph_format.left_indent = Inches(0.6)
                    #paragraph_format.line_spacing=0.8
                    r.style.name = clauseObj.doc_style
                    r.style.font.size=11
                    r.style.font.name ='宋体'

        document.save(path+agreementData.name+".docx")

        file = open(path+agreementData.name+".docx", "rb")

        attachment.search([('res_model', '=', 'agreement.download.doc')]).unlink()

        attachment = attachment.create({
            'name': agreementData.name,
            'datas': base64.encodestring(file.read()),
            'datas_fname': agreementData.name+".docx",
            'res_model': 'agreement.download.doc',
            'res_id': self.id
        })
        file.close()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/%s?download=true'  % (attachment.id,),
        }
        print(111)

    def Import_doc(self):
        full_path = self.file_path
        doc = Document(full_path)
        agreement_id=self._context['active_id']   #读取当前合同ID

        recital = self.env['agreement.recital']  # 叙述
        section = self.env['agreement.section']  # 章节
        clause = self.env['agreement.clause']  # 条款
        appendix = self.env['agreement.appendix']  # 附录

        vals = []
        # 每一段的内容
        i = 0
        for para in doc.paragraphs:
            val = {}
            val['agreement_id']=agreement_id
            val['name'] = i
            val['title'] = ""
            val['sequence'] = i
            val['content'] = para.text
            val['doc_text'] = para.text
            val['doc_style'] = para.style.name
            val['doc_font'] = para.style.font.name
            if i==13:
                val['content'] = "xxxxxx"
                val['doc_text'] = "xxxxx"
            vals.append(val)
            i = i + 1
        recitalVals = []  #叙述 Data

        sectionVals=[]   #章节 Data

        clauseVals=[]    #条款  Data

        section_title="" # 章节  标题
        section_no=1  #.章节
        for val in vals:
            if val['sequence']<=23:
                #叙述
                recitalVals.append(val)
            elif val['sequence']==24:
                #章节  定义
                section_title="1"
                val['title'] = section_title
                sectionVals.append(val)
            elif val['sequence'] > 24 and val['sequence']<32:
                #章节-条款   定义
                val['title'] = section_title+"."+str(section_no)
                val['section_id']=24
                clauseVals.append(val)
                section_no=section_no+1
            elif val['sequence'] == 32:
                # 章节  甲方责任
                section_no=1
                section_title = "2"
                val['title'] = section_title
                sectionVals.append(val)
            elif val['sequence'] > 32 and val['sequence'] < 39:
                # 章节-条款  甲方责任
                val['title'] = section_title+"."+str(section_no)
                val['section_id'] = 32
                clauseVals.append(val)
                section_no = section_no + 1

            elif val['sequence'] == 39:
                # 章节  乙方责任
                section_no = 1
                section_title = "3"
                val['title'] = section_title
                sectionVals.append(val)
            elif val['sequence'] > 39 and val['sequence'] < 45:
                # 章节-条款  乙方责任
                val['title'] = section_title + "." + str(section_no)
                val['section_id'] = 39
                clauseVals.append(val)
                section_no = section_no + 1
            elif val['sequence'] == 45:
                # 章节  4.	价款、付款和税金
                section_no = 1
                section_title = "4"
                val['title'] = section_title
                sectionVals.append(val)
            elif val['sequence'] > 45 and val['sequence'] < 49:
                # 章节-条款
                val['title'] = section_title + "." + str(section_no)
                val['section_id'] = 45
                clauseVals.append(val)
                section_no = section_no + 1
            elif val['sequence'] == 49:
                # 章节  实施服务
                section_no = 1
                section_title = "5"
                val['title'] = section_title
                sectionVals.append(val)
            elif val['sequence'] > 49 and val['sequence'] < 54:
                # 章节-条款  实施服务
                val['title'] = section_title + "." + str(section_no)
                val['section_id'] = 49
                clauseVals.append(val)
                section_no = section_no + 1

            else:
                print(1)

        #叙述
        recital.search([('agreement_id', '=', agreement_id)]).unlink()
        recital.create(recitalVals)

        #章节
        section.search([('agreement_id', '=', agreement_id)]).unlink()
        section.create(sectionVals)

        #条款
        sectionListData=section.search([('agreement_id', '=', agreement_id)])
        for sectionObj in sectionListData:
            for val in clauseVals:
                if sectionObj.sequence == val['section_id']:
                    val['section_id']=sectionObj.id

        clause.create(clauseVals)

        return True