# -*- coding: utf-8 -*-
import logging
import io
import base64
from odoo import api, fields, models, _
from odoo.tests.common import Form
from PIL import Image
_logger = logging.getLogger(__name__)

try:
    from aip import AipOcr
except ImportError:
    _logger.error('Odoo module e2yun_business_card depends on the baidu-aip python module')
    AipOcr = None

class ImportContactImportWizard(models.TransientModel):
    _name = 'contact.import.wizard'
    _description = 'Import Your contact from webcam.'

    card_image = fields.Binary(attachment=True,
                          help="This field holds the image used as image for the card, limited to 1024x1024px.")

    # @api.multi
    # def _import_facturx_invoice(self, tree):
    #     ''' Extract invoice values from the Factur-x xml tree passed as parameter.
    #
    #     :param tree: The tree of the Factur-x xml file.
    #     :return: A dictionary containing account.invoice values to create/update it.
    #     '''
    #     amount_total_import = None
    #
    #     # type must be present in the context to get the right behavior of the _default_journal method (account.invoice).
    #     # journal_id must be present in the context to get the right behavior of the _default_account method (account.invoice.line).
    #     self_ctx = self.with_context(type='in_invoice')
    #     journal_id = self_ctx._default_journal().id
    #     self_ctx = self_ctx.with_context(journal_id=journal_id)
    #
    #     # self could be a single record (editing) or be empty (new).
    #     with Form(self_ctx, view='account.invoice_supplier_form') as invoice_form:
    #
    #         # Partner (first step to avoid warning 'Warning! You must first select a partner.').
    #         elements = tree.xpath('//ram:SellerTradeParty/ram:SpecifiedTaxRegistration/ram:ID', namespaces=tree.nsmap)
    #         partner = elements and self.env['res.partner'].search([('vat', '=', elements[0].text)], limit=1)
    #         if not partner:
    #             elements = tree.xpath('//ram:SellerTradeParty/ram:Name', namespaces=tree.nsmap)
    #             partner_name = elements and elements[0].text
    #             partner = elements and self.env['res.partner'].search([('name', 'ilike', partner_name)], limit=1)
    #         if not partner:
    #             elements = tree.xpath('//ram:SellerTradeParty//ram:URIID[@schemeID=\'SMTP\']', namespaces=tree.nsmap)
    #             partner = elements and self.env['res.partner'].search([('email', '=', elements[0].text)], limit=1)
    #         if partner:
    #             invoice_form.partner_id = partner
    #
    #         # Reference.
    #         elements = tree.xpath('//rsm:ExchangedDocument/ram:ID', namespaces=tree.nsmap)
    #         if elements:
    #             invoice_form.reference = elements[0].text
    #
    #         # Name.
    #         elements = tree.xpath('//ram:BuyerOrderReferencedDocument/ram:IssuerAssignedID', namespaces=tree.nsmap)
    #         if elements:
    #             invoice_form.name = elements[0].text
    #
    #         # Comment.
    #         elements = tree.xpath('//ram:IncludedNote/ram:Content', namespaces=tree.nsmap)
    #         if elements:
    #             invoice_form.comment = elements[0].text
    #
    #         # Refund type.
    #         # There is two modes to handle refund in Factur-X:
    #         # a) type_code == 380 for invoice, type_code == 381 for refund, all positive amounts.
    #         # b) type_code == 380, negative amounts in case of refund.
    #         # To handle both, we consider the 'a' mode and switch to 'b' if a negative amount is encountered.
    #         elements = tree.xpath('//rsm:ExchangedDocument/ram:TypeCode', namespaces=tree.nsmap)
    #         type_code = elements[0].text
    #         refund_sign = 1
    #
    #         # Total amount.
    #         elements = tree.xpath('//ram:GrandTotalAmount', namespaces=tree.nsmap)
    #         if elements:
    #             total_amount = float(elements[0].text)
    #
    #             # Handle 'b' refund mode.
    #             if total_amount < 0 and type_code == '380':
    #                 refund_sign = -1
    #
    #             # Currency.
    #             if elements[0].attrib.get('currencyID'):
    #                 currency_str = elements[0].attrib['currencyID']
    #                 currency = self.env.ref('base.%s' % currency_str.upper(), raise_if_not_found=False)
    #                 if currency != self.env.user.company_id.currency_id and currency.active:
    #                     invoice_form.currency_id = currency
    #
    #                 # Store xml total amount.
    #                 amount_total_import = total_amount * refund_sign
    #
    #         # Date.
    #         elements = tree.xpath('//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString', namespaces=tree.nsmap)
    #         if elements:
    #             date_str = elements[0].text
    #             date_obj = datetime.strptime(date_str, DEFAULT_FACTURX_DATE_FORMAT)
    #             invoice_form.date_invoice = date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #
    #         # Due date.
    #         elements = tree.xpath('//ram:SpecifiedTradePaymentTerms/ram:DueDateDateTime/udt:DateTimeString',
    #                               namespaces=tree.nsmap)
    #         if elements:
    #             date_str = elements[0].text
    #             date_obj = datetime.strptime(date_str, DEFAULT_FACTURX_DATE_FORMAT)
    #             invoice_form.date_due = date_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #
    #         # Invoice lines.
    #         elements = tree.xpath('//ram:IncludedSupplyChainTradeLineItem', namespaces=tree.nsmap)
    #         if elements:
    #             for element in elements:
    #                 with invoice_form.invoice_line_ids.new() as invoice_line_form:
    #
    #                     # Sequence.
    #                     line_elements = element.xpath('.//ram:AssociatedDocumentLineDocument/ram:LineID',
    #                                                   namespaces=tree.nsmap)
    #                     if line_elements:
    #                         invoice_line_form.sequence = int(line_elements[0].text)
    #
    #                     # Product.
    #                     line_elements = element.xpath('.//ram:SpecifiedTradeProduct/ram:Name', namespaces=tree.nsmap)
    #                     if line_elements:
    #                         invoice_line_form.name = line_elements[0].text
    #                     line_elements = element.xpath('.//ram:SpecifiedTradeProduct/ram:SellerAssignedID',
    #                                                   namespaces=tree.nsmap)
    #                     if line_elements and line_elements[0].text:
    #                         product = self.env['product.product'].search([('default_code', '=', line_elements[0].text)])
    #                         if product:
    #                             invoice_line_form.product_id = product
    #                     if not invoice_line_form.product_id:
    #                         line_elements = element.xpath('.//ram:SpecifiedTradeProduct/ram:GlobalID',
    #                                                       namespaces=tree.nsmap)
    #                         if line_elements and line_elements[0].text:
    #                             product = self.env['product.product'].search([('barcode', '=', line_elements[0].text)])
    #                             if product:
    #                                 invoice_line_form.product_id = product
    #
    #                     # Quantity.
    #                     line_elements = element.xpath('.//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity',
    #                                                   namespaces=tree.nsmap)
    #                     if line_elements:
    #                         invoice_line_form.quantity = float(line_elements[0].text) * refund_sign
    #
    #                     # Price Unit.
    #                     line_elements = element.xpath('.//ram:GrossPriceProductTradePrice/ram:ChargeAmount',
    #                                                   namespaces=tree.nsmap)
    #                     if line_elements:
    #                         invoice_line_form.price_unit = float(line_elements[0].text) / invoice_line_form.quantity
    #                     else:
    #                         line_elements = element.xpath('.//ram:NetPriceProductTradePrice/ram:ChargeAmount',
    #                                                       namespaces=tree.nsmap)
    #                         if line_elements:
    #                             invoice_line_form.price_unit = float(line_elements[0].text) / invoice_line_form.quantity
    #
    #                     # Discount.
    #                     line_elements = element.xpath('.//ram:AppliedTradeAllowanceCharge/ram:CalculationPercent',
    #                                                   namespaces=tree.nsmap)
    #                     if line_elements:
    #                         invoice_line_form.discount = float(line_elements[0].text)
    #
    #                     # Taxes
    #                     line_elements = element.xpath(
    #                         './/ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:RateApplicablePercent',
    #                         namespaces=tree.nsmap)
    #                     invoice_line_form.invoice_line_tax_ids.clear()
    #                     for tax_element in line_elements:
    #                         percentage = float(tax_element.text)
    #
    #                         tax = self.env['account.tax'].search([
    #                             ('company_id', '=', invoice_form.company_id.id),
    #                             ('amount_type', '=', 'percent'),
    #                             ('type_tax_use', '=', 'purchase'),
    #                             ('amount', '=', percentage),
    #                         ], limit=1)
    #
    #                         if tax:
    #                             invoice_line_form.invoice_line_tax_ids.add(tax)
    #         elif amount_total_import:
    #             # No lines in BASICWL.
    #             with invoice_form.invoice_line_ids.new() as invoice_line_form:
    #                 invoice_line_form.name = invoice_form.comment or '/'
    #                 invoice_line_form.quantity = 1
    #                 invoice_line_form.price_unit = amount_total_import
    #
    #         # Refund.
    #         invoice_form.type = 'in_refund' if refund_sign == -1 else 'in_invoice'
    #
    #     return invoice_form.save()


    @api.multi
    def _get_contact_from_aipocr(self, image):
        contact= {}
        if AipOcr:
            APP_ID = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_app_id', '16224769')

            API_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_app_key', 'FFG6BEOxGDnK7Dynslzfxpl1')

            SECRET_KEY = self.env['ir.config_parameter'].sudo().get_param(
                'baidu_secret_key', '0vYlPKcUEqMA0kerjhRoQNWU0uiBCoTF')
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
            result = client.businessCard(image, options);
        return result

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    @api.multi
    def _create_contact_from_file(self, attachment):

        contact_form = Form(self.env['res.partner'], view='crm.view_partners_form_crm1')
        imagedata = base64.b64decode(attachment)
        result = self._get_contact_from_aipocr(imagedata)
        if result['words_result_num'] > 0:
            contact = result['words_result']
            if ((contact['NAME'] and contact['NAME'] != [''])
                    or (contact['MOBILE']and contact['MOBILE'] != [''])):
                [name] = contact['NAME']
                [mobile] = contact['MOBILE']
                if contact['COMPANY'] and contact['COMPANY'] != ['']:

                    [company] = contact['COMPANY']
                    partner = self.env['res.partner'].search(
                        [('name', 'ilike', name),
                        ('parent_name', 'ilike', company)], limit=1)
                elif contact['EMAIL'] and contact['EMAIL'] != ['']:
                    [email] = contact['EMAIL']
                    partner = self.env['res.partner'].search(
                        [('name', 'ilike', name),
                         ('email', '=', email)], limit=1)
                if not partner: #如果不存在，新建联系人
                    #contact['FAX']
                    if contact['TEL'] and contact['TEL'] != ['']:
                        [contact_form.phone] = contact['TEL']
                    if contact['NAME'] and contact['NAME'] != ['']:
                        [contact_form.name] = contact['NAME']
                    if contact['TITLE'] and contact['TITLE']!=['']:
                        [contact_form.title] = contact['TITLE']
                    if contact['MOBILE'] and contact['MOBILE'] != ['']:
                        [contact_form.mobile] = contact['MOBILE']
                    if contact['EMAIL'] and contact['EMAIL'] != ['']:
                        [contact_form.email] = contact['EMAIL']
                    #contact['PC']
                    if contact['URL'] and contact['URL'] != ['']:
                        [contact_form.website] = contact['URL']
                    if contact['ADDR'] and contact['ADDR'] != ['']:
                        street = ''
                        for item in contact['ADDR']:
                            street += item
                        contact_form.street = street
                    if contact['COMPANY'] and contact['COMPANY'] != ['']:
                        [company] = contact['COMPANY']
                        partner = self.env['res.partner'].search([('name', 'ilike', company),('company_type','=','company')], limit=1)
                        if not partner:
                            partner = self.env['res.partner'].create({'name': company,
                                                                      'company_type': 'company',
                                                                      'street': contact_form.street,
                                                                      'website': contact_form.website})
                        contact_form.parent_id = partner
                    contact_form.image = attachment
                    partner = contact_form.save()

                    image = self.env['ir.attachment'].create({
                        'name': 'Business Card: '+partner.name,
                        'res_id': partner.id,
                        'res_model': 'res.partner',
                        'datas': attachment,
                        'datas_fname': partner.name + '.jpeg',
                        'description': partner.name + partner.phone + partner.email,
                        'type': 'binary',
                    })
                    partner.message_post(attachment_ids=[image.id])
                    return partner
                else: #修改现有联系人信息
                    modify={}
                    if contact['TEL'] and contact['TEL'] != [''] and [partner.phone] != contact['TEL']:
                        [modify['phone']] = contact['TEL']
                    if contact['TITLE'] and contact['TITLE'] != [''] and [partner.title] != contact['TITLE']:
                        [modify['title']] = contact['TITLE']
                    if contact['MOBILE'] and contact['MOBILE'] != [''] and [partner.mobile] != contact['MOBILE']:
                        [modify['mobile']] = contact['MOBILE']
                    if contact['EMAIL'] and contact['EMAIL'] != [''] and [partner.email] != contact['EMAIL']:
                        [modify['email']] = contact['EMAIL']
                    if contact['URL'] and contact['URL'] != [''] and [partner.website] != contact['URL']:
                        [modify['website']] = contact['URL']
                    street = ''
                    if contact['ADDR'] and contact['ADDR'] != ['']:
                        for item in contact['ADDR']:
                            street += item
                    if street != '' and partner.street != street:
                        modify['street'] = street
                    if modify:
                        partner.write(modify)

                        image = self.env['ir.attachment'].create({
                            'name': 'Business Card: '+ partner.name,
                            'res_id': partner.id,
                            'res_model': 'res.partner',
                            'datas': attachment,
                            'datas_fname': partner.name + '.jpeg',
                            'description': partner.name + partner.phone + partner.email,
                            'type': 'binary',
                        })

                        partner.message_post(attachment_ids=[image.id])
                        return partner
        return False

    @api.multi
    def create_contact(self):
        ''' Create the contact from file.
         :return: A action redirecting to contact form view.
        '''
        if not self.card_image:
            return

        contact = self._create_contact_from_file(self.card_image)
        if not contact:
            return
        action_vals = {
            'name': _('Contact'),
            'domain': [('id', 'in', contact.ids)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'res_id': contact.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return action_vals
