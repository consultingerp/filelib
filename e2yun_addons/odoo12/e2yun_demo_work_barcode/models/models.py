# -*- coding: utf-8 -*-

from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

class e2yun_demo_work_barcode(models.Model):
    _inherit = 'ck.routing.sync'

    def print_qr_code(self):
        return self.env.ref('e2yun_demo_work_barcode.report_qrcode_ck_routing_sync').report_action(self)

    def compute_qr_code(self):
        self.ck_qrcode2 = self.fworkcenterno + '/' + self.foperno

    ck_qrcode2 = fields.Binary('QR Code', compute='compute_qr_code')

    # @api.onchange('fworkcenterno')
    # @api.onchange('foperno')
    # def print_qr_code(self):
    #     code = self.fworkcenterno + '/' + self.foperno
    #     qr = qrcode.QRCode(
    #         version=2,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=1
    #     )
    #     qr.add_data(code)
    #     qr.make(fit=True)
    #     img = qr.make_image()
    #     temp = BytesIO()
    #     img.save(temp, format="PNG")
    #     qr_image = base64.b64encode(temp.getvalue())
    #     self.ck_qrcode = qr_image

    # ck_qrcode = fields.Binary('QR Code', attachment=True)

class E2yunDemoWorkQRcode2(models.Model):
    _inherit = 'ck.icmo.sync'

    def print_qr_code(self):
        return self.env.ref('e2yun_demo_work_barcode.report_qrcode_ck_icmo_sync').report_action(self)

# class CK_Hours_Worker_line(models.Model):
#     _inherit = 'ck.hours.worker.line'
#
#     @api.multi
#     def unlink(self):
#         for r in self:
#             r.order_id.unlink()
#         return True
