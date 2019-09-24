# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re


class E2yunCrmGroupsExtends(models.Model):
    _inherit = 'res.users'

    @api.model
    def write(self, vals):
        # vals_delete_groups 变量中的KV，都是需要应用本函数进行处理的 删除的权限项
        vals_delete_groups = {}
        delete_groups_ids = []
        for item in vals.items():
            if re.findall('in_group_', item[0]):
                if item[1] == False:
                    delete_groups_ids.append(int(item[0][9:]))
                else:
                    continue
            else:
                continue
        if len(delete_groups_ids) > 0:
            # 在这里执行逻辑，遍历vals_delete_groups
            # 将in_group转化为res.groups对象
            delete_groups = self.env['res.groups'].browse(delete_groups_ids)

            # 递归实现
            def implied_groups_delete(inner_delete_groups):
                for group_item in inner_delete_groups:
                    if group_item.implied_ids:
                        implied_groups_delete(group_item.implied_ids)
                    else:
                        delete_group_name_string = 'in_group_' + str(group_item.id)
                        vals[delete_group_name_string] = False
            # item.implied_ids
            implied_groups_delete(delete_groups)
            # 查看要操作的权限组中，有没有继承项，有的话，递归遍历，取出所有要取消的权限组，
            # 转化成in_group形式，加到vals中去
            res = super(E2yunCrmGroupsExtends, self).write(vals)
            return res
        else:
            return super(E2yunCrmGroupsExtends, self).write(vals)
