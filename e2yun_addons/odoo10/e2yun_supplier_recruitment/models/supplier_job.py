# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SupplierJob(models.Model):
    _name = "supplier.job"
    _description = " Supplier Job Position"
    _inherit = ["mail.alias.mixin", "mail.thread"]
    name = fields.Char(string='Job Title', required=True, index=True, translate=True)
    expected_suppliers = fields.Integer(compute='_compute_suppliers', string='Total Forecasted Suppliers', store=True,
                                        help='Expected number of Supplier for this job position after new recruitment.')
    no_of_supplier = fields.Integer(compute='_compute_suppliers', string="Current Number of Supplier", store=True,
                                    help='Number of suppliers currently occupying this job position.')
    no_of_recruitment = fields.Integer(string='Expected New Supplier', copy=False,
                                       help='Number of new suppliers you expect to recruit.', default=1)
    no_of_certified_supplier = fields.Integer(string='Certified Supplier', copy=False,
                                          help='Number of certified suppliers for this job position during recruitment phase.')
    supplier_ids = fields.One2many('product.supplierinfo', 'job_id', string='Supplier', groups='base.group_user')
    description = fields.Text(string='Supplier Job Description')
    requirements = fields.Text('Requirements')
    product_id = fields.Many2one('product.template', string='Product')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='recruit',
        help="Set whether the recruitment process is open or closed for this supplier job position.")

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, product_id)',
         'The name of the job position must be unique per product in company!'),
    ]

    @api.depends('no_of_recruitment', 'supplier_ids.job_id', 'supplier_ids.active')
    def _compute_suppliers(self):
        suppliers_data = self.env['product.supplierinfo'].read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in suppliers_data)
        for job in self:
            job.no_of_supplier = result.get(job.id, 0)
            job.expected_suppliers = result.get(job.id, 0) + job.no_of_recruitment

    @api.model
    def create(self, values):
        """ We don't want the current user to be follower of all created job """
        return super(SupplierJob, self.with_context(mail_create_nosubscribe=True)).create(values)

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(SupplierJob, self).copy(default=default)

    @api.multi
    def set_recruit(self):
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            record.write({'state': 'recruit', 'no_of_recruitment': no_of_recruitment})
        return True

    @api.multi
    def set_open(self):
        return self.write({
            'state': 'open',
            'no_of_recruitment': 0,
            'no_of_certified_supplier': 0
        })

    @api.model
    def _default_address_id(self):
        return self.env.user.company_id.partner_id

    address_id = fields.Many2one(
        'res.partner', "Job Location", default=_default_address_id,
        help="Address where suppliers are working")
    application_ids = fields.One2many('supplier.applicant', 'job_id', "Applications")
    application_count = fields.Integer(compute='_compute_application_count', string="Applications")
    manager_id = fields.Many2one('hr.employee', string='Manager', track_visibility='onchange')
    user_id = fields.Many2one('res.users', "Recruitment Responsible", track_visibility='onchange')
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Applications")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Documents")
    alias_id = fields.Many2one(
        'mail.alias', "Alias", ondelete="restrict", required=True,
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")
    color = fields.Integer("Color Index")

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.supplier_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'supplier.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'supplier.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'supplier.applicant':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment

        for job in self:
            job.document_ids = result[job.id]
            job.documents_count = len(job.document_ids)

    @api.multi
    def _compute_application_count(self):
        read_group_result = self.env['supplier.applicant'].read_group([('job_id', '=', self.id)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        for job in self:
            job.application_count = result.get(job.id, 0)

    def get_alias_model_name(self, vals):
        return 'supplier.applicant'

    def get_alias_values(self):
        values = super(SupplierJob, self).get_alias_values()
        values['alias_defaults'] = {'job_id': self.id}
        return values

    @api.model
    def create(self, vals):
        return super(SupplierJob, self.with_context(mail_create_nolog=True)).create(vals)

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'open':
            return 'e2yun_supplier_recruitment.mt_job_new_supplier'
        return super(SupplierJob, self)._track_subtype(init_values)

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('e2yun_supplier_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = ['|', '&', ('res_model', '=', 'supplier.job'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'supplier.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action

    @api.multi
    def action_set_no_of_recruitment(self, value):
        return self.write({'no_of_recruitment': value})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
