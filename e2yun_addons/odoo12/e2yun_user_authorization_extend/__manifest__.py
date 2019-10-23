# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 e2yun - http://www.e2yun.com
#    All Rights Reserved.
#    info@e2yun.com
############################################################################
#    Coded by: joytao (joytao.zhu@e2yun.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "E2yun User Authorization Extend",
    "version": "8.0.1.0.2",
    "author": "Joytao, lth",
    "website": "www.e2yun.cn",
    "category": "Base",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "views/res_groups_view.xml",
        "wizard/generate_model_access_view.xml",
        "wizard/generate_rule_groups_view.xml"
    ],
    "installable": True
}
