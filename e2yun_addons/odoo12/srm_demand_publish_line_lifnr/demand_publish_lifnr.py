# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _

class mat_demand_line_details_lifnr(models.Model):
    _name = 'mat.demand.line.batch.confim.lifnr'

    def batch_confirmation(self):
        is_supplier = self.env['res.users']._get_default_supplier()
        cr=self._cr
        for id in self._context['active_ids']:
          mat_obj = self.env['mat.demand.line.details'].browse(id)
          vals = {}
          vals['lifnr'] = mat_obj.lifnr.id
          vals['matnr'] = mat_obj.matnr.id
          vals['ddate'] = mat_obj.ddate
          vals['id'] = mat_obj.id
          vals['mat_demand_id'] = mat_obj.mat_demand_id.id


          if is_supplier != 0:
              vals['state'] = 'supplier_confirm'
              sql = " update mat_demand_line_details set bmeng="+str(mat_obj.menge)+", state='supplier_confirm' where id=" + str(id) + "  "
              cr.execute(sql)
          else:
              vals['state'] = 'purchase_confirm'
              sql=" update mat_demand_line_details set  state='purchase_confirm',delivery='t' where id="+str(id)+" and state in('supplier_confirm','supplier_edit')  "
              cr.execute(sql)
          self.env['mat.demand.line.details'].insert_mat_demand_line_details(vals)