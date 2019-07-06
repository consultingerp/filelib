# -*- coding: utf-8 -*-
import logging
from .transform import four_point_transform
import cv2
import numpy
import imutils
import json
from . import imgenhance
import base64
from odoo import api, fields, models, _
#from odoo.tests.common import Form
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


def preProcess(image):
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)

    grayImage  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gaussImage = cv2.GaussianBlur(grayImage, (5, 5), 0)
    edgedImage = cv2.dilate(gaussImage, numpy.ones((3, 3), numpy.uint8), iterations=2)
    edgedImage = cv2.erode(edgedImage, numpy.ones((2, 2), numpy.uint8), iterations=3)
    edgedImage = cv2.Canny(edgedImage, 70, 200)

    cnts = cv2.findContours(edgedImage.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    screenCnt = {}
    for c in cnts:
        peri = cv2.arcLength(c, True)  # Calculating contour circumference
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            if (abs(round((approx[0][0][0] - approx[1][0][0]) / image.shape[0])) == 1 or
                abs(round((approx[2][0][1] - approx[0][0][1]) / image.shape[1])) == 1):
                screenCnt = approx
                break


    return screenCnt, ratio


class ImportContactImportWizard(models.TransientModel):
    _name = 'contact.import.wizard'
    _description = _('Import Your Contacts from Files..')

    attachment_ids = fields.Many2many('ir.attachment', string=_('Cards Files'))

    @api.multi
    def _correct_image(self, image):

        screenCnt, ratio = preProcess(image)
        if len(screenCnt) > 0:
            warped = four_point_transform(image, screenCnt.reshape(4, 2) * ratio)
            enhancer = imgenhance.Enhancer()
            return enhancer.sharp(warped, 4.0)
        return {}

    @api.multi
    def _get_logo_image(self, image):
        result = self._get_contact_from_aipimageclassify(image)
        if 'error_code' in result:
            return False,{}
        if 'result_num' in result and result['result_num'] > 0:
            area = 0
            for item in result['result']:
                if round(item['probability']) == 1:
                    if item['location']['width'] * item['location']['height'] > area:
                        area = item['location']['width'] * item['location']['height']
                        left = item['location']['left']
                        top = item['location']['top']
                        right = item['location']['left'] + item['location']['width']
                        buttom = item['location']['top'] + item['location']['height']
                        name = item['name']
                    if area > 0:
                        return name, cv2.imdecode(numpy.fromstring(image, numpy.uint8), cv2.IMREAD_COLOR)[top:buttom, left:right]
        return False, {}

    @api.multi
    def _get_contact_from_aipimageclassify(self, image):
        try:
            from aip import AipImageClassify
        except ImportError:
            _logger.error(_('Odoo module e2yun_cards_ocr depends on the baidu-aip python module.'))
            raise UserError(_('Odoo module e2yun_cards_ocr depends on the baidu-aip python module.'))

        result = {}
        if AipImageClassify:
            APP_ID = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_image_app_id', '16288732')

            API_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_image_app_key', 'WhPQFWBWpzNtb3Y23xBIaXyW')

            SECRET_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_image_secret_key', 'ibuLCnBoUVAdsAYID8ApA6XcQDsLHkLp')
            options = {}
            options["custom_lib"] = "false"
            client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
            result = client.logoSearch(image, options)
        return result

    @api.multi
    def _get_contact_from_aipocr(self, image):
        try:
            from aip import AipOcr
        except ImportError:
            _logger.error(_('Odoo module e2yun_cards_ocr depends on the baidu-aip python module.'))
            raise UserError(_('Odoo module e2yun_cards_ocr depends on the baidu-aip python module.'))

        result= {}
        if AipOcr:
            APP_ID = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_ocr_app_id', '16224769')

            API_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_ocr_app_key', 'FFG6BEOxGDnK7Dynslzfxpl1')

            SECRET_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_ocr_secret_key', '0vYlPKcUEqMA0kerjhRoQNWU0uiBCoTF')
            options = {}
            options["detect_direction"] = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_detect_direction', "true")
            options["probability"] = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_probability',"true")
            options["detect_language"] = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_detect_language',"true")
            options["language_type"] = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_language_type',"CHN_ENG")
            client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
            result = client.businessCard(image, options)
            result2 = client.basicAccurate(image, options)
        return result,result2

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    @api.multi
    def _create_contact_from_file(self, attachment):

        contact_obj = self.env['res.partner']
        contact_value = {}
        company = ''
        imagedata = base64.b64decode(attachment.datas)
        image_tmp = cv2.imdecode(numpy.fromstring(imagedata, numpy.uint8), cv2.IMREAD_COLOR)
        image = self._correct_image(image_tmp)
        if len(image) > 0:
            img_encode = cv2.imencode('.jpeg', image)[1]
            imagedata = numpy.array(img_encode).tostring()
            attachment.datas = base64.b64encode(imagedata)
        result,result1 = self._get_contact_from_aipocr(imagedata)
        if 'error_code' in result and 'error_code' in result1:
            attachment.write({'name': _('Business Card: OCR Fail'),
                              'datas_fname': attachment.datas_fname,
                              'description': _('OCR Fail'),
                              })
            return {}
        if 'words_result_num' in result and result['words_result_num'] > 0:
            contact = result['words_result']
            if (contact['NAME'] and contact['NAME'] != ['']):
                res = ''
                i = 0
                for item in contact['NAME']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['name'] = res

            if (contact['MOBILE'] and contact['MOBILE'] != ['']):
                res = ''
                i = 0
                for item in contact['MOBILE']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['mobile'] = res
            if (contact['COMPANY'] and contact['COMPANY'] != ['']):
                res = ''
                i = 0
                for item in contact['COMPANY']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                company = res
            if (contact['TEL'] and contact['TEL'] != ['']):
                res = ''
                i = 0
                for item in contact['TEL']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['phone'] = res
            if (contact['TITLE'] and contact['TITLE'] != ['']):
                res = ''
                i = 0
                for item in contact['TITLE']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['function'] = res
            if (contact['EMAIL'] and contact['EMAIL'] != ['']):
                res = ''
                i = 0
                for item in contact['EMAIL']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['email'] = res
            if (contact['URL'] and contact['URL'] != ['']):
                res = ''
                i = 0
                for item in contact['URL']:
                    if i == 0:
                        res += item
                        i += 1
                    else:
                        res += ',' + item
                contact_value['website'] = res
            if (contact['ADDR'] and contact['ADDR'] != ['']):
                res = ''
                for item in contact['ADDR']:
                        res += item
                contact_value['street'] = res
        if 'words_result_num' in result1 and result1['words_result_num'] > 0:
            info = result1['words_result']
            res= ''
            i = 0
            for item in info:
                if item['words'] and item['probability']['average'] > 0.8:
                    if not contact_value.get('name' ,False):
                        contact_value['name'] = item['words']

                    if i == 0:
                        res = item['words']

                    else:
                        res = res + ',' + item['words']
                    i += 1
            if res != '':
                contact_value['comment'] = res
        if contact_value.get('name',False):
            # company = contact_value.get('company',False)
            name = contact_value.get('name',False)
            partner = False
            if company != '' and name:
                partner = self.env['res.partner'].search(
                    [('name', 'ilike', name),
                     ('parent_name', 'ilike', company)], limit=1)
            elif contact_value.get('email',False):
                partner = self.env['res.partner'].search(
                    [('name', 'ilike', name),
                     ('email', '=', contact_value.get('email',False))], limit=1)

            contact_value['image'] = attachment.datas
            if not partner:  # 如果不存在，新建联系人

                parent_partner = False
                company_name = False
                logo_image = False
                if company != '':
                    parent_partner = self.env['res.partner'].search(
                        [('name', 'ilike', company), ('is_company', '=', True)], limit=1)
                if not parent_partner :
                    company_name, logo_image = self._get_logo_image(imagedata)
                    if company_name and logo_image.any():
                        parent_partner = self.env['res.partner'].search(
                            [('name', 'ilike', company_name), ('is_company', '=', True)], limit=1)
                if not parent_partner and (company != '' or company_name):
                    if company_name:
                        logo_datas = cv2.imencode('.jpg', logo_image)[1].tostring()
                        parent_partner = self.env['res.partner'].create({
                            'name': company if company != '' else company_name,
                            'is_company': True,
                            'image': base64.b64encode(logo_datas),
                            'street': contact_value.get('street',''),
                            'website': contact_value.get('website','')})
                    else:
                        parent_partner = self.env['res.partner'].create({
                            'name': company if company != '' else company_name,
                            'is_company': True,
                            'street': contact_value.get('street', ''),
                            'website': contact_value.get('website', '')})
                if parent_partner:
                    if not parent_partner.image and logo_image:
                        logo_datas = cv2.imencode('.jpg', logo_image)[1].tostring()
                        parent_partner.image = base64.b64encode(logo_datas)

                    contact_value['parent_id'] = parent_partner.id

                partner = contact_obj.create(contact_value)

                attachment.write({'name': 'Business Card: ' + partner.name,
                                  'res_id': partner.id,
                                  'res_model': 'res.partner',
                                  'datas_fname': partner.name + '.jpeg',
                                  'description': partner.name + partner.phone if partner.phone else '' +
                                                                partner.email if partner.email else '',
                                  })
                partner.message_post(attachment_ids=[attachment.id])
            else:  # 修改现有联系人信息

                partner.write(contact_value)
                attachment.write({'name': 'Business Card: ' + partner.name,
                                  'res_id': partner.id,
                                  'res_model': 'res.partner',
                                  'datas_fname': partner.name + '.jpeg',
                                  'description': partner.name + partner.phone if partner.phone else '' +
                                                                partner.email if partner.email else '',
                                  })
                partner.message_post(attachment_ids=[attachment.id])
            return partner
        return {}

    # @api.multi
    # def _create_contact_from_file(self, attachment):
    #
    #     contact_form = Form(self.env['res.partner'], view='crm.view_partners_form_crm1')
    #     imagedata = base64.b64decode(attachment.datas)
    #     image_tmp = cv2.imdecode(numpy.fromstring(imagedata, numpy.uint8), cv2.IMREAD_COLOR)
    #     image = self._correct_image(image_tmp)
    #     if len(image) > 0:
    #         img_encode = cv2.imencode('.jpeg', image)[1]
    #         imagedata = numpy.array(img_encode).tostring()
    #         attachment.datas = base64.b64encode(imagedata)
    #     result = self._get_contact_from_aipocr(imagedata)
    #     if 'error_code' in result:
    #         attachment.write({'name': 'Business Card: test',
    #                           'datas_fname':  'test.jpeg',
    #                           'description': 'test',
    #                           })
    #         return {}
    #     if 'words_result_num' in result and result['words_result_num'] > 0:
    #         contact = result['words_result']
    #         if ((contact['NAME'] and contact['NAME'] != [''])
    #                 or (contact['MOBILE']and contact['MOBILE'] != [''])):
    #             name = ''
    #             i = 0
    #             for item in contact['NAME']:
    #                 if i == 0:
    #                     name += item
    #                     i += 1
    #                 else:
    #                     name += ',' + item
    #             contact_form.name = name
    #             [name] = contact['NAME']
    #             mobile = ''
    #             i = 0
    #             for item in contact['MOBILE']:
    #                 if i == 0:
    #                     mobile += item
    #                     i += 1
    #                 else:
    #                     mobile += ',' + item
    #             contact_form.mobile = mobile
    #             company = False
    #             partner = False
    #             if contact['COMPANY'] and contact['COMPANY'] != ['']:
    #
    #                 [company] = contact['COMPANY']
    #                 partner = self.env['res.partner'].search(
    #                     [('name', 'ilike', name),
    #                     ('parent_name', 'ilike', company)], limit=1)
    #             elif contact['EMAIL'] and contact['EMAIL'] != ['']:
    #                 [email] = contact['EMAIL']
    #                 partner = self.env['res.partner'].search(
    #                     [('name', 'ilike', name),
    #                      ('email', '=', email)], limit=1)
    #             if not partner: #如果不存在，新建联系人
    #                 #contact['FAX']
    #
    #                 if contact['TEL'] and contact['TEL'] != ['']:
    #                     phone = ''
    #                     i = 0
    #                     for item in contact['TEL']:
    #                         if i==0:
    #                             phone +=  item
    #                             i += 1
    #                         else:
    #                             phone += ',' + item
    #                     contact_form.phone = phone
    #
    #
    #
    #                 if contact['TITLE'] and contact['TITLE']!=['']:
    #                     title =''
    #                     i = 0
    #                     for item in contact['TITLE']:
    #                         if i == 0:
    #                             title += item
    #                             i += 1
    #                         else:
    #                             title += ',' + item
    #                     contact_form.title = title
    #
    #                 if contact['EMAIL'] and contact['EMAIL'] != ['']:
    #                     [contact_form.email] = contact['EMAIL']
    #                 #contact['PC']
    #                 if contact['URL'] and contact['URL'] != ['']:
    #                     [contact_form.website] = contact['URL']
    #                 if contact['ADDR'] and contact['ADDR'] != ['']:
    #                     street = ''
    #                     for item in contact['ADDR']:
    #                         street += item
    #                     contact_form.street = street
    #                 parent_partner = False
    #
    #                 if company:
    #                     parent_partner = self.env['res.partner'].search([('name', 'ilike', company),('is_company','=',True)], limit=1)
    #                 if not parent_partner:
    #
    #                     company_name,logo_image = self._get_logo_image(imagedata)
    #
    #                     parent_partner = self.env['res.partner'].create({'name': company if company else company_name,
    #                                                               'is_company': True,
    #                                                               'street': contact_form.street,
    #                                                               'website': contact_form.website})
    #                     if company_name and logo_image.any():
    #                         logo_datas = cv2.imencode('.jpg', logo_image)[1].tostring()
    #                         parent_partner.image = base64.b64encode(logo_datas)
    #
    #                 contact_form.parent_id = parent_partner
    #                 contact_form.image = attachment.datas
    #                 partner = contact_form.save()
    #                 attachment.write({'name': 'Business Card: '+partner.name,
    #                                   'res_id': partner.id,
    #                                   'res_model': 'res.partner',
    #                                   'datas_fname': partner.name + '.jpeg',
    #                                   'description': partner.name + partner.phone if partner.phone else '' +
    #                                                  partner.email if partner.email else '',
    #                                   })
    #                 partner.message_post(attachment_ids=[attachment.id])
    #                 return partner
    #             else: #修改现有联系人信息
    #                 modify={}
    #                 if contact['TEL'] and contact['TEL'] != [''] and [partner.phone] != contact['TEL']:
    #                     [modify['phone']] = contact['TEL']
    #                 if contact['TITLE'] and contact['TITLE'] != [''] and [partner.title] != contact['TITLE']:
    #                     [modify['title']] = contact['TITLE']
    #                 # if contact['MOBILE'] and contact['MOBILE'] != [''] and [partner.mobile] != contact['MOBILE']:
    #                 #     [modify['mobile']] = contact['MOBILE']
    #                 if contact['EMAIL'] and contact['EMAIL'] != [''] and [partner.email] != contact['EMAIL']:
    #                     [modify['email']] = contact['EMAIL']
    #                 if contact['URL'] and contact['URL'] != [''] and [partner.website] != contact['URL']:
    #                     [modify['website']] = contact['URL']
    #                 street = ''
    #                 if contact['ADDR'] and contact['ADDR'] != ['']:
    #                     for item in contact['ADDR']:
    #                         street += item
    #                 if street != '' and partner.street != street:
    #                     modify['street'] = street
    #                 if modify:
    #                     modify['image'] = attachment.datas
    #                     partner.write(modify)
    #                     attachment.write({'name': 'Business Card: ' + partner.name,
    #                                       'res_id': partner.id,
    #                                       'res_model': 'res.partner',
    #                                       'datas_fname': partner.name + '.jpeg',
    #                                       'description': partner.name + partner.phone if partner.phone else '' +
    #                                                  partner.email if partner.email else '',
    #                                       })
    #                     partner.message_post(attachment_ids=[attachment.id])
    #                     return partner
    #     return {}

    @api.multi
    def create_contacts(self):
        ''' Create the contacts from files.
         :return: A action redirecting to contact form view.
        '''
        if not self.attachment_ids:
            return
        contacts = self.env['res.partner']
        for attachment in self.attachment_ids:
            contact =self._create_contact_from_file(attachment)
            if len(contact):
                contacts += contact
        if len(contacts) < 1:
            return
        action_vals = {
            'name': _('Contacts'),
            'domain': [('id', 'in', contacts.ids)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(contacts) == 1:
            action_vals.update({'res_id': contacts[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals
