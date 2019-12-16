# -*- coding: utf-8 -*-

import base64
import sys
from odoo import api, fields, models, tools, _
from docx import Document
from docx.shared import Pt,Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re
from win32com.client import Dispatch, DispatchEx
import pythoncom
import os, sys
import difflib
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




        paragraphs = doc.paragraphs
       #paragraphs[6].text = "小Z同学："
        #paragraphs[6].add('some striked', strike=True)
        val = {}
        val['testxml'] =paragraphs[6]._element.xml
        wdel = '<w: delw: id="0"w: author="pactera"w: date="2019-12-02T15:56:00Z"><w: rw: rsidDel="00C410A9"><w: rPr><w: rFontsw: ascii="华文中宋"w: eastAsia="华文中宋"w: hAnsi="华文中宋"w: hint="eastAsia"/><w: szw: val="32"/><w: szCsw: val="32"/></w: rPr><w: delText>北京海辉高科软件有限公司</w: delText></w: r></w: del>'
        #num = xml.find('合同号')
        #str(doc.element.xml).replace(str(doc.element.xml)[num], "徐初秋")
        #paragraphs[6]._element.xml = val['testxml']
        #doc.Comments.Add(Range=doc.paragraphs[6].Range, Text='注释') #其中我的i写的是遍历整个段落，然后匹配出需要加注释的地方

        doc.save('D:\\demo1207.docx')
        vals=[]
       # 每一段的内容
        i=0
        for para in doc.paragraphs:
            print(i)
            val = {}
            val['no'] =i
            if para.text=='实施服务协议':
                print(1)
            val['text']=para.text
            val['style_font'] = para.style.font.name
            val['style_name'] = para.style.name
            val['style'] = para.style
            val['font'] = para.style.font
            vals.append(val)
            i=i+1

        document = Document() # 初始化文档
        for val in vals:
            print(val)
            if val['style_name'] and val['style_name']=='文档标题':
                d_title = document.add_heading(val['text'], 0)
                d_title.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
                d_title.style=val['style']
                #d_title.style.font.size=28
                #d_title.bold = True

            else:
              p=document.add_paragraph(val['text'])
              p.style=val['style']

        document.save('D:\\demo1203.docx')

        return True



class AgreementDownloadDoc(models.Model):
    _name = "agreement.download.doc"

    file_path = fields.Char('File Path')

    #默认样式设置
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

     try:
        path = sys.path[0]+"\\"

        agreement_id=self._context['active_id']

        attachment = self.env['ir.attachment'] # 附件

        agreement = self.env['agreement']

        agreementData = agreement.browse(agreement_id)

        agreement_word_data = self.env['agreement.word.data']  # wordData

        clauseListData = agreement_word_data.search([('agreement_id', '=', agreement_id),('detail','=',False),('the_editor','=',True)])

        master_word_id=0

        if clauseListData:
            master_word_id=clauseListData[0].master_word_id
        else:
            clauseListData = agreement_word_data.search(
                [('agreement_id', '=', agreement_id), ('detail', '=', False)])
            master_word_id = clauseListData[0].master_word_id

        pythoncom.CoInitialize()
        wordApp = Dispatch('Word.Application')  # 打开word应用程序
        wordApp.Visible = 0  # 后台运行,不显示
        wordApp.DisplayAlerts = 0  # 不警告

        datas=self.env['ir.http'].binary_content(
            xmlid=None, model='ir.attachment', id=master_word_id ,field='datas', unique=None, filename=None,
            filename_field='datas_fname', download='true', mimetype='',
            default_mimetype=None, related_id=None, access_mode=None,
            access_token=None,
            env=self.env)
        wb_path=path+agreementData.name+".docx"

        f = open(wb_path, "wb")
        datass = base64.decodestring(datas[2])
        f.write(datass)
        f.close()

        doc = wordApp.Documents.Open(FileName=wb_path, Encoding='gbk')
        try:
              for clauseObj in clauseListData:  # 条款
                  para = doc.Paragraphs[clauseObj.sequence]
                  if clauseObj.the_editor==True:
                         para.Range.Find.Execute(clauseObj.old_text, False, False, False, False, False, False, 0, True,
                                                 clauseObj.new_text, 1)
                    # oldStr= re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", para.Range.text)
                    # newStr= re.sub('[a-zA-Z0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+', "", clauseObj.content)
                    # if oldStr != newStr:
                    #   opcodes = difflib.SequenceMatcher(None, oldStr, newStr).get_opcodes()
                    #   for op, af, at, bf, bt in opcodes:
                    #       if op == 'delete':
                    #           #para.Range.Find.Execute(oldStr[af:at], False, False, False, False, False, True, 1, True,newStr[bf:bt], 2)
                    #           para.Range.Find.Execute(oldStr, False, False, False, False, False, False, 0, True,
                    #                                   newStr, 1)
                    #       elif op == 'replace' and (oldStr[af:at] and newStr[bf:bt]):
                    #           oldStr=oldStr[af:at]
                    #           newStr=newStr[bf:bt]
                    #           para.Range.Find.Execute(oldStr, False, False, False, False, False, False, 0, True,
                    #                                                newStr, 1)
                    #       elif op == 'insert':
                    #           para.Range.Find.Execute(oldStr, False, False, False, False, False, False, 0, True,
                    #                                   newStr, 1)

              doc.SaveAs(r"" + wb_path)
        except BaseException as e:
            print(e)
            if os.path.exists(wb_path):
                os.remove(wb_path)
            doc.Close()

        else:
            doc.Close()
        file = open(wb_path, "rb")
        attachment.search([('res_model', '=', 'agreement.download.doc'), ('id', '!=', master_word_id)]).unlink()  #删除无效附件
        attachmentObj=attachment.create({
            'name': agreementData.name,
            'datas': base64.encodestring(file.read()),
            'datas_fname': agreementData.name+".docx",
            'res_model': 'agreement.download.doc',
            'res_id': self.id
        })
        file.close()

        if os.path.exists(wb_path):
            os.remove(wb_path)

     finally:
       return {
             'type': 'ir.actions.act_url',
             'target': 'new',
             'url': 'web/content/%s?download=true' % (attachmentObj.id),
       }
       print(111)


    def Import_doc(self):
        full_path = self.file_path
        pythoncom.CoInitialize()  #多线程处理
        wordApp = Dispatch('Word.Application')  # 打开word应用程序
        wordApp.Visible = 0         # 后台运行,不显示
        wordApp.DisplayAlerts = 0  # 不警告
        doc = wordApp.Documents.Open(FileName=full_path, Encoding='gbk')
        agreement_id=self._context['active_id']   #读取当前合同ID
        agreement_word_data = self.env['agreement.word.data']  # wordData
        attachment = self.env['ir.attachment']  # 附件

        #记录当前合同的母版word
        file = open(full_path, "rb")
        attachment.search([('res_model', '=', 'agreement.download.doc')]).unlink()
        attachment_id=attachment.create({
            'name': '',
            'datas': base64.encodestring(file.read()),
            'datas_fname': "",
            'res_model': 'agreement.download.doc',
            'res_id': self.id
        })
        file.close()

        vals = []
        # 每一段的内容
        i = 0
        # 利用下标遍历段落
        allContent=""
        for i in range(len(doc.Paragraphs)):
            para = doc.Paragraphs[i]
            val = {}
            val['agreement_id']=agreement_id
            val['sequence'] = i
            if para.Range.text or  para.Range.text!="":
                font_size=para.Range.Font.Size;
                if font_size>20:
                    font_size=11
                val['alignment'] = para.Range.ParagraphFormat.Alignment  # 0,1,2 分别对应左对齐、居中、右对齐
                val['font_Name'] = para.Range.Font.Name
                val['font_size'] = font_size
                val['content'] = para.Range.text
                if para.Range.ParagraphFormat.Alignment==1:
                    p = "<p id=" + str(i) + " style = 'text-align: center; font-size: "+str(font_size)+"px;'>"
                elif  para.Range.ParagraphFormat.Alignment==2:
                    p = "<p id=" + str(i) + " style = 'text-align: center; font-size: " + str(font_size) + "px;'>"
                else:
                    p = "<p id=" + str(i) + " style ='font-size: " + str(font_size) + "px;'>"
                content = p + para.Range.text + "</p>"
            else:
                content="<br/>"
            allContent=allContent+content
            val['master_word_id']=attachment_id.id
            vals.append(val)




        agreement_word_data.search([('agreement_id', '=', agreement_id)]).unlink()
        agreement_word_data.create(vals)
        val=vals[0]
        val['content']=allContent
        val['detail'] = True
        vals=[]
        vals.append(val)
        agreement_word_data.create(vals)
        return True