# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from datetime import datetime

class mat_demand_line_details(models.Model):
    _inherit ='mat.demand.line.details'
    _table = 'mat_demand_line_details'
    _order = ' id desc '

    # def fields_get(self):
    #
    #     fields_to_hide = ['pdate']
    #     res = super(models.Model, self).fields_get(self)
    #     user = self.env['res.users'].browse(self._uid)
    #     is_supplier = self.env['res.users']._get_default_supplier()
    #     for field in fields_to_hide:
    #       if not is_supplier==0:
    #           res[field]['invisible'] = 1
    #       #del res[field];  # 删除键是'Name'的条目
    #     return res



    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Performs a ``search()`` followed by a ``read()``.

        :param domain: Search domain, see ``args`` parameter in ``search()``. Defaults to an empty domain that will match all records.
        :param fields: List of fields to read, see ``fields`` parameter in ``read()``. Defaults to all fields.
        :param offset: Number of records to skip, see ``offset`` parameter in ``search()``. Defaults to 0.
        :param limit: Maximum number of records to return, see ``limit`` parameter in ``search()``. Defaults to no limit.
        :param order: Columns to sort result, see ``order`` parameter in ``search()``. Defaults to no sort.
        :return: List of dictionaries containing the asked fields.
        :rtype: List of dictionaries.

        """

        cr = self._cr
        is_supplier = self.env['res.users']._get_default_supplier()
        sql_max_id = "select  max(id) as id  from mat_demand_head where 1=1  and history_data='False' "
        cr.execute(sql_max_id)
        max_id = cr.fetchone()
        list_temp = []
        if domain and domain[0][0] == 'mat_demand_id' and domain[0][2] == -1:
            if max_id:
                del domain[0]
                list_temp.append('mat_demand_id')
                list_temp.append('=')
                list_temp.append(max_id[0])
                domain.append(list_temp)

        if is_supplier and is_supplier != 0:
            list_temp = []
            list_temp.append('lifnr')
            list_temp.append('=')
            list_temp.append(is_supplier)
            domain.append(list_temp)

            list_temp = []
            list_temp.append('publish')
            list_temp.append('=')
            list_temp.append('t')
            domain.append(list_temp)

        list_temp = []
        list_temp.append('state')
        list_temp.append('<>')
        list_temp.append('delete')
        domain.append(list_temp)


        records = self.search(domain or [], offset=offset, limit=limit, order=order)

        if not records:
            return []

        if fields and fields == ['id']:
            # shortcut read if we only want the ids
            return [{'id': record.id} for record in records]

        # read() ignores active_test, but it would forward it to any downstream search call
        # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
        # was presumably only meant for the main search().
        # TODO: Move this to read() directly?
        if 'active_test' in self._context:
            context = dict(self._context)
            del context['active_test']
            records = records.with_context(context)

        result = records.read(fields)
        if len(result) <= 1:
            return result

        # reorder read
        index = {vals['id']: vals for vals in result}
        return [index[record.id] for record in records if record.id in index]


    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #
    #     cr = self._cr
    #     is_supplier = self.env['res.users']._get_default_supplier()
    #     sql_max_id = "select  max(id) as id  from mat_demand_head where 1=1  and history_data='False' "
    #     cr.execute(sql_max_id)
    #     max_id = cr.fetchone()
    #     list_temp = []
    #     if domain and domain[0][0] == 'mat_demand_id' and domain[0][2] == -1:
    #         if max_id:
    #             del domain[0]
    #             list_temp.append('mat_demand_id')
    #             list_temp.append('=')
    #             list_temp.append(max_id[0])
    #             domain.append(list_temp)
    #
    #     if is_supplier and is_supplier != 0:
    #         list_temp = []
    #         list_temp.append('lifnr')
    #         list_temp.append('=')
    #         list_temp.append(is_supplier)
    #         domain.append(list_temp)
    #
    #         list_temp = []
    #         list_temp.append('publish')
    #         list_temp.append('=')
    #         list_temp.append('t')
    #         domain.append(list_temp)
    #
    #     list_temp = []
    #     list_temp.append('state')
    #     list_temp.append('<>')
    #     list_temp.append('delete')
    #     domain.append(list_temp)
    #
    #     records = self.search(domain or [], offset=offset, limit=limit, order=order)
    #     if not records:
    #         return []
    #
    #     if fields and fields == ['id']:
    #         # shortcut read if we only want the ids
    #         return [{'id': record.id} for record in records]
    #
    #     # read() ignores active_test, but it would forward it to any downstream search call
    #     # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
    #     # was presumably only meant for the main search().
    #     # TODO: Move this to read() directly?
    #     if 'active_test' in self._context:
    #         context = dict(self._context)
    #         del context['active_test']
    #         records = records.with_context(context)
    #
    #     result = records.read(fields)
    #     if len(result) <= 1:
    #         return result
    #
    #     # reorder read
    #     index = {vals['id']: vals for vals in result}
    #     return [index[record.id] for record in records if record.id in index]


    def batch_confirmation(self, cr, uid, ids, context=None):
        print(ids)
