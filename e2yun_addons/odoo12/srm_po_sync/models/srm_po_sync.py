#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
class srm_pyrfc_config(models.Model):
    _name = "srm.po.sync"

    start_date = fields.Date('start date')
    ending_date = fields.Date('ending date')
    ebeln = fields.Char('ebeln')

    # def search_read(self, cr, uid, domain, fields=None, offset=0, limit=None, order=None, context=None):
    #
    #     list_temp = []
    #     list_temp.append('create_uid')
    #     list_temp.append('=')
    #     list_temp.append(uid)
    #     domain.append(list_temp)
    #     record_ids = self.search(cr, uid, domain or [], offset=offset, limit=limit, order=order, context=context)
    #
    #     if not record_ids:
    #         return []
    #     if fields and fields == ['id']:
    #         return [{'id': id} for id in record_ids]
    #     read_ctx = dict(context or {})
    #     read_ctx.pop('active_test', None)
    #     result = self.read(cr, uid, record_ids, fields, context=read_ctx)
    #     if len(result) <= 1:
    #         return result
    #     index = dict((r['id'], r) for r in result)
    #     return [index[x] for x in record_ids if x in index]

    def srm_po_sync_m(self,ids, context=None):
        IV_BEGIN=''
        IV_END=''
        EBELNS=[]
        cr = self._cr
        uid = self._uid

        for id in ids['active_ids']:
            sql = "select * from srm_po_sync WHERE id=" + str(id) + ""
            cr.execute(sql)
            k=cr.dictfetchone()
            if k['ebeln']:
                EBELNS.append(k['ebeln'])
            elif k['start_date'] and  k['ending_date']:
                IV_BEGIN= k['start_date'].replace('-','')
                IV_END=k['ending_date'].replace('-','')
                break
        try:
            if not IV_BEGIN=='' or len(EBELNS)>0:
                self.env['srm.po.sync.task'].srm_po_sync_task_m(IV_BEGIN,IV_END,EBELNS,'MENU')
        except BaseException as  e:
            raise  UserError(e)
        finally:
            sql="delete from srm_po_sync where ebeln is null and start_date is null and ending_date is null "
            cr.execute(sql)
