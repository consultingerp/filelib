# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
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

import sys
from datetime import datetime
# import datetime
# from openerp.osv import orm, fields
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)
_loglvl = _logger.getEffectiveLevel()
SEP = '|'


class import_odbc_dbtable(models.Model):
    _name = "import.odbc.dbtable"
    _description = 'Import Table Data'
    _order = 'exec_order'

    name = fields.Char('Datasource name', required=True, size=64)
    enabled = fields.Boolean('Execution enabled', default=True)
    dbsource_id = fields.Many2one('base.external.dbsource',
                                   'Database source', required=True)
    sql_source = fields.Text('SQL', required=True,
                              help='Column names must be valid \
                              "import_data" columns.')
    model_target = fields.Many2one('ir.model', 'Target object')
    noupdate = fields.Boolean('No updates',
                               help="Only create new records;\
                               disable updates to existing records.")
    exec_order = fields.Integer('Execution order',
                                 help="Defines the order to perform \
                                 the import", default=10)
    last_sync = fields.Datetime('Last sync date',
                                 help="Datetime for the last succesfull \
                                 sync. \nLater changes on the source may \
                                 not be replicated on the destination")
    start_run = fields.Datetime('Time started', readonly=True)
    last_run = fields.Datetime('Time ended', readonly=True)
    last_record_count = fields.Integer('Last record count',
                                        readonly=True)
    last_error_count = fields.Integer('Last error count', readonly=True)
    last_warn_count = fields.Integer('Last warning count', readonly=True)
    last_log = fields.Text('Last run log', readonly=True)
    ignore_rel_errors = fields.Boolean('Ignore relationship errors',
                                        help="On error try to reimport \
                                        rows ignoring relationships.")
    raise_import_errors = fields.Boolean('Raise import errors',
                                          help="Import errors not \
                                          handled, intended for \
                                          debugging purposes. \nAlso \
                                          forces debug messages to be \
                                          written to the server log.")

    _defaults = {
        'enabled': True,
        'exec_order': 10,
    }

    def import_data(self, model_obj, cols, data, noupdate=False):
        """import data to model filed"""
        if noupdate:
            pass
        else:
            data_dict = {}
            for i in range(len(cols)):
                if cols[i] == 'kunnr':
                    ss = self.env['crm.team'].search([('shop_code', '=', data[i])]).id
                    dict1 = {cols[i]: ss}
                else:
                    dict1 = {cols[i]: data[i]}
                data_dict.update(dict1)
            model_obj.create(data_dict)

    def _import_data(self, flds, data, model_obj, table_obj, log):
        """Import data and returns error msg or empty string"""

        def find_m2o(field_list):
            """"Find index of first column with a one2many field"""
            for i, x in enumerate(field_list):
                if len(x) > 3 and x[-3:] == ':id' or x[-3:] == '/id':
                    return i
            return -1

        def append_to_log(log, level, obj_id='', msg='', rel_id=''):
            if '_id_' in obj_id:
                obj_id = ('.'.join(obj_id.split('_')[:-2]) + ': ' +
                          obj_id.split('_')[-1])
            if ': .' in msg and not rel_id:
                rel_id = msg[msg.find(': .')+3:]
                if '_id_' in rel_id:
                    rel_id = ('.'.join(rel_id.split('_')[:-2]) +
                              ': ' + rel_id.split('_')[-1])
                    msg = msg[:msg.find(': .')]
            log['last_log'].append('%s|%s\t|%s\t|%s' % (level.ljust(5),
                                   obj_id, rel_id, msg))

        _logger.debug(data)
        cols = list(flds)  # copy to avoid side effects
        errmsg = str()
        if table_obj.raise_import_errors:
            model_obj.create()
            table_obj.import_data(model_obj, cols, data,
                                  noupdate=table_obj.noupdate)
        else:
            try:
                table_obj.import_data(model_obj, cols, data, noupdate=table_obj.noupdate)
            except:
                errmsg = str(sys.exc_info()[1])
        if errmsg and not table_obj.ignore_rel_errors:
            # Fail
            append_to_log(log, 'ERROR', data, errmsg)
            log['last_error_count'] += 1
            return False
        if errmsg and table_obj.ignore_rel_errors:
            # Warn and retry ignoring many2one fields...
            append_to_log(log, 'WARN', data, errmsg)
            log['last_warn_count'] += 1
            # Try ignoring each many2one
            # (tip: in the SQL sentence select more problematic FKs first)
            i = find_m2o(cols)
            if i >= 0:
                # Try again without the [i] column
                del cols[i]
                del data[i]
                self._import_data(cols, data, model_obj,
                                  table_obj, log)
            else:
                # Fail
                append_to_log(log, 'ERROR', data,
                              'Removed all m2o keys and still fails.')
                log['last_error_count'] += 1
                return False
        return True

    def import_run(self):
        # db_model = self.pool.get('base.external.dbsource')
        db_model = self.env['base.external.dbsource']
        actions = self.read(['id', 'exec_order'])
        actions.sort(key=lambda x: (x['exec_order'], x['id']))

        # Consider each dbtable:
        for action_ref in actions:
            obj = self.browse(action_ref['id'])
            # if not obj.enabled:
            #     continue  # skip

            _logger.setLevel(obj.raise_import_errors and
                             logging.DEBUG or _loglvl)
            _logger.debug('Importing %s...' % obj.name)

            # now() microseconds are stripped
            # to avoid problem with SQL smalldate
            # TODO: convert UTC Now to local timezone
            # http://stackoverflow.com/questions/4770297/python-convert-utc-datetime-string-to-local-datetime
            model_name = obj.model_target.model
            # model_obj = self.pool.get(model_name)
            model_obj = self.env[model_name]
            xml_prefix = model_name.replace('.', '_') + "_id_"
            log = {'start_run': datetime.now().replace(microsecond=0),
                   'last_run': None,
                   'last_record_count': 0,
                   'last_error_count': 0,
                   'last_warn_count': 0,
                   'last_log': list()}
            self.write(log)

            # Prepare SQL sentence; replace "%s" with the last_sync date
            if obj.last_sync:
                sync = datetime.strptime(str(obj.last_sync), "%Y-%m-%d %H:%M:%S")
            else:
                sync = datetime(1900, 1, 1, 0, 0, 0)
            params = {'sync': sync}
            res = db_model.browse(obj.dbsource_id.id).execute(obj.sql_source, params, metadata=True)

            # Exclude columns titled "None"; add (xml_)"id" column
            cidx = ([i for i, x in enumerate(res['cols'])
                    if x.upper() != 'NONE'])
            cols = ([x for i, x in enumerate(res['cols'])
                    if x.upper() != 'NONE'] + ['ID'])

            # Import each row:
            for row in res['rows']:
                # Build data row;
                # import only columns present in the "cols" list
                data = list()
                for i in cidx:
                    # TODO: Handle imported datetimes properly
                    #       convert from localtime to UTC!
                    v = row[i]
                    if isinstance(v, str):
                        v = v.strip()
                    data.append(v)
                data.append(xml_prefix + str(row[0]).strip())

                # Import the row; on error, write line to the log
                log['last_record_count'] += 1
                self._import_data(cols, data, model_obj, obj, log)
                if log['last_record_count'] % 500 == 0:
                    _logger.info('...%s rows processed...'
                                 % (log['last_record_count']))

            # Finished importing all rows
            # If no errors, write new sync date
            if not (log['last_error_count'] or log['last_warn_count']):
                log['last_sync'] = log['start_run']
            level = logging.DEBUG
            if log['last_warn_count']:
                level = logging.WARN
            if log['last_error_count']:
                level = logging.ERROR
            _logger.log(level,
                        'Imported %s , %d rows, %d errors, %d warnings.' %
                        (model_name, log['last_record_count'],
                            log['last_error_count'],
                            log['last_warn_count']))
            # Write run log, either if the table import is active or inactive
            if log['last_log']:
                log['last_log'].insert(0,
                                       'LEVEL|== Line ==    |== Relationship \
                                       ==|== Message ==')
            log.update({'last_log': '\n'.join(log['last_log'])})
            log.update({'last_run': datetime.now().replace(microsecond=0)})
            self.write(log)


        # Finished
        _logger.debug('Import job FINISHED.')
        return True

    def import_schedule(self):
        # cron_obj = self.pool.get('ir.cron')
        cron_obj = self.env['ir.cron']
        new_create_id = cron_obj.create({
            'name': 'Import ODBC tables',
            'interval_type': 'hours',
            'interval_number': 1,
            'numbercall': -1,
            'model': 'import.odbc.dbtable',
            'function': 'import_run',
            'doall': False,
            'active': True
            })
        return {
            'name': 'Import ODBC tables',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'ir.cron',
            'res_id': new_create_id,
            'type': 'ir.actions.act_window',
            }
