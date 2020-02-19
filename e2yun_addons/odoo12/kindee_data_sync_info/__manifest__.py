# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPO_SE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Kindee Data Sync Info ',
    'version': '0.1',
    'category': 'Report Work Management',
    'author': 'Feng Zhou',
    'application': True,
    'depends': ['base', 'base_external_dbsource', 'import_odbc','decimal_precision',],
    'data': ['security/report_work_security.xml',
             'security/ir.model.access.csv',
             'views/hours_worker_data.xml',
             'views/data.xml',
             # 'report/ck_hours_worker_analysis_view.xml',
             'views/decimal_precision_data.xml',
             # 'report_four/ck_hours_worker_report_view.xml',
             'batchapprove/work_batch_approve.xml',
             # 'report_summary/ck_working_summary_report_view.xml',
             ],
    'js': [

    ],
    'qweb': [
        'static/src/xml/qweb.xml',
             ],
    'installable': True,
    'web': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
