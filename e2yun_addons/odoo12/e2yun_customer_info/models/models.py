# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import pytz
import logging
from odoo.exceptions import UserError
from odoo.tools.translate import _

from email.utils import formataddr

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')

logger = logging.getLogger(__name__)


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


# put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


class e2yun_customer_info(models.Model):
    _name = 'e2yun.customer.info'

    def _default_category(self):
        return self.env['res.partner.category'].browse(self._context.get('category_id'))

    def _default_company(self):
        return self.env['res.company']._company_default_get('res.partner')

    name = fields.Char(index=True)
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    date = fields.Date(index=True)
    title = fields.Many2one('res.partner.title')
    parent_id = fields.Many2one('e2yun.customer.info', string='Related Company', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('e2yun.customer.info', 'parent_id', string='Contacts', domain=[
        ('active', '=', True)])  # force "active_test" domain to bypass _search() override
    ref = fields.Char(string='Internal Reference', index=True)
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang,
                            help="All the emails and documents sent to this contact will be translated in this language.")
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="The partner's timezone, used to output proper date and time values "
                               "inside printed reports. It is important to set a value for this field. "
                               "You should use the same timezone that is otherwise used to pick and "
                               "render date and time values: your computer's timezone.")
    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)
    user_id = fields.Many2one('res.users', string='Salesperson',
                              help='The internal user in charge of this contact.')
    vat = fields.Char(string='Tax ID',
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    bank_ids = fields.One2many('res.partner.bank', 'partner_id', string='Banks')
    website = fields.Char()
    comment = fields.Text(string='Notes')

    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                   column2='category_id', string='Tags', default=_default_category)
    credit_limit = fields.Float(string='Credit Limit')
    barcode = fields.Char(oldname='ean13', help="Use a barcode to identify this contact from the Point of Sale.")
    active = fields.Boolean(default=True)
    customer = fields.Boolean(string='Is a Customer', default= False,
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Is a Vendor',
                              help="Check this box if this contact is a vendor. It can be selected in purchase orders.")
    employee = fields.Boolean(help="Check this box if this contact is an Employee.")
    function = fields.Char(string='Job Position')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Other address'),
         ("private", "Private Address"),
         ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
    email_formatted = fields.Char(
        'Formatted Email', compute='_compute_email_formatted',
        help='Format email address "Name <email@domain>"')
    phone = fields.Char()
    mobile = fields.Char()
    is_company = fields.Boolean(string='Is a Company', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    industry_id = fields.Many2one('res.partner.industry', 'Industry')
    # company_type is only an interface field, do not use it in business logic
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    compute='_compute_company_type', inverse='_write_company_type')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=_default_company)
    color = fields.Integer(string='Color Index', default=0)
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True)
    partner_share = fields.Boolean(
        'Share Partner', compute='_compute_partner_share', store=True,
        help="Either customer (not a user), either shared user. Indicated the current partner is a customer without "
             "access or with a limited access created for sharing data.")
    contact_address = fields.Char(compute='_compute_contact_address', string='Complete Address')

    # technical field used for managing commercial fields
    commercial_partner_id = fields.Many2one('e2yun.customer.info', compute='_compute_commercial_partner',
                                            string='Commercial Entity', store=True, index=True)
    commercial_company_name = fields.Char('Company Name Entity', compute='_compute_commercial_company_name',
                                          store=True)
    company_name = fields.Char('Company Name')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px", )
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")
    # hack to allow using plain browse record in qweb views, and used in ir.qweb.field.contact
    self = fields.Many2one(comodel_name=_name, compute='_compute_get_ids')

    partner_id = fields.Many2one('res.partner', company_dependent=True, string='Normal Customer')

    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
                                               string='Customer Payment Terms',
                                               help="This payment term will be used instead of the default one for sales orders and customer invoices",
                                               oldname="property_payment_term")

    team_id = fields.Many2one('crm.team', 'Team')

    parent_team_id = fields.Many2one(comodel_name='crm.team', compute='_compute_parent_team_id', store=True)

    # 新增客户中的字段
    customer_id = fields.Char('	Customer Id')
    x_studio_name_en_1 = fields.Char('Name_En')
    x_studio_account_group = fields.Char('Account Group')
    parent_account = fields.Many2one('res.partner', company_dependent=True, string='母公司')
    x_studio_account_type = fields.Selection([["Target Client", "Target Client"], ["Active Client", "Active Client"],
                                              ["Significant Client", "Significant Client"]], 'Account type')
    activity_user_id = fields.Many2one('res.users', company_dependent=True, string='责任用户')
    x_studio__1 = fields.Selection(
        [["华中", "华中"], ["华东", "华东"], ["西南", "西南"], ["华南", "华南"], ["华北", "华北"], ["东北", "东北"], ["西北", "西北"],
         ["Greater China", "Greater China"], ["Japan", "Japan"], ["Asia Pacific", "Asia Pacific"], ["Europe", "Europe"],
         ["North America", "North America"], ["Rest of World", "Rest of World"]], 'Account Region')
    x_studio_ = fields.Selection(
        [["客户类型", "T&M contract,by Month/by Quarter billing"], ["行业1", "FP by Milestone billing"],
         ["银行", "pay after project is completed and project cycle<2 months"],
         ["制造业", "pay after project is completed and project cycle>2 months"]], 'Way of settlement')
    x_studio_ender_customer = fields.Char('Ender Customer')
    x_studio_account_management = fields.Selection([["NMA", "NMA"], ["CMA", "CMA"]], 'Account Management')
    x_studio_account_source = fields.Selection([["Other", "Other"]], 'Account Source')
    x_studio_registration_address = fields.Char('Registration Address')
    grade_id = fields.Many2one('res.partner.grade', 'Level')
    secondary_industry_ids = fields.Many2many(
        comodel_name='res.partner.industry', string="Secondary Industries",
        domain="[('id', '!=', industry_id)]")
    x_studio__2 = fields.Integer('Number of employees')
    x_studio_revenue_forcast_for_future_4q = fields.Float('Revenue forcast for future 4Q')
    property_product_pricelist = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    x_studio_is_new_logo = fields.Boolean('Is New LOGO')
    is_strategic = fields.Boolean(string='Is Strategic')
    x_studio_is_a_public_company = fields.Selection([["YES", "YES"]], string='Is Strategic')
    x_studio_annual_revenue = fields.Float('Annual Revenue')
    x_studio_ipo_location = fields.Char('IPO Location')
    x_studio_stock_code = fields.Char('Stock Code')
    x_studio_annual_profitusdk = fields.Float('Annual Profit（USDK）')
    x_studio_market_value = fields.Float('Market Value')

    state = fields.Selection([
        ('Draft', '新建'),
        ('done', '完成')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='Draft')

    register_no = fields.Char('Registration number')

    _sql_constraints = [
        ('check_name', "CHECK( (type='contact' AND name IS NOT NULL) or (type!='contact') )",
         'Contacts require a name.'),
        ('name_unique', 'unique(name)', "The name you entered already exists"),
        ('register_no_unique', 'unique(register_no)', "The Duty paragraph you entered already exists"),
    ]

    @api.onchange('name')
    def onchange_name(self):
        name = self.name
        count = self.env['res.partner'].sudo().search_count([('name', '=', name)])
        if count > 0:
            self.name = False
            msg = _("The name you entered already exists for customers.")
            return {
                'warning': {
                    'title': _('Tips'),
                    'message': msg
                }
            }

    @api.onchange('register_no')
    def onchange_register_no(self):
        register_no = self.register_no
        if register_no:
            count = self.env['res.partner'].sudo().search_count([('register_no', '=', register_no)])
            if count > 0:
                self.vat = False
                msg = _("The Duty paragraph you entered already exists for customers.")
                return {
                    'warning': {
                        'title': _('Tips'),
                        'message': msg
                    }
                }

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else 'person'

    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        self.env.cr.execute("""
        WITH RECURSIVE cpid(id, parent_id, commercial_partner_id, final) AS (
            SELECT
                id, parent_id, id,
                (coalesce(is_company, false) OR parent_id IS NULL) as final
            FROM e2yun_customer_info
            WHERE id = ANY(%s)
        UNION
            SELECT
                cpid.id, p.parent_id, p.id,
                (coalesce(is_company, false) OR p.parent_id IS NULL) as final
            FROM e2yun_customer_info p
            JOIN cpid ON (cpid.parent_id = p.id)
            WHERE NOT cpid.final
        )
        SELECT cpid.id, cpid.commercial_partner_id
        FROM cpid
        WHERE final AND id = ANY(%s);
        """, [self.ids, self.ids])

        d = dict(self.env.cr.fetchall())
        for partner in self:
            fetched = d.get(partner.id)
            if fetched is not None:
                partner.commercial_partner_id = fetched
            elif partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

    @api.depends('tz')
    def _compute_tz_offset(self):
        for partner in self:
            partner.tz_offset = datetime.datetime.now(pytz.timezone(partner.tz or 'GMT')).strftime('%z')

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_address(self):
        for partner in self:
            partner.contact_address = partner._display_address()

    @api.depends('company_name', 'parent_id.is_company', 'commercial_partner_id.name')
    def _compute_commercial_company_name(self):
        for partner in self:
            p = partner.commercial_partner_id
            partner.commercial_company_name = p.is_company and p.name or partner.company_name

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.is_company = (self.company_type == 'company')

    @api.one
    def _compute_get_ids(self):
        self.self = self.id

    @api.one
    @api.depends('team_id')
    def _compute_parent_team_id(self):
        self.parent_team_id = self.team_id.parent_id.id

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return self._address_fields() + [
            'country_id.address_format', 'country_id.code', 'country_id.name',
            'company_name', 'state_id.code', 'state_id.name',
        ]

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)

    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'

    @api.depends('name', 'email')
    def _compute_email_formatted(self):
        for partner in self:
            if partner.email:
                partner.email_formatted = formataddr((partner.name or u"False", partner.email or u"False"))
            else:
                partner.email_formatted = ''

    @api.multi
    def _display_address(self, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    @api.model
    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return self._address_fields()

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return self._formatting_address_fields() + [
            'country_id.address_format', 'country_id.code', 'country_id.name',
            'company_name', 'state_id.code', 'state_id.name',
        ]

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"

    @api.model
    def _get_address_format(self):
        return self.country_id.address_format or self._get_default_address_format()

    @api.multi
    def _get_country_name(self):
        return self.country_id.name or ''

    def customer_transfer_to_normal(self):
        self.ensure_one()
        data = {}
        UNINCLUDE_COL = ['bank_ids', 'user_ids', 'state', 'commercial_partner_id', 'child_ids', 'parent_id',
                         'partner_id', 'display_name', 'tz_offset', 'lang', 'tz', 'self', 'id', 'create_uid',
                         'create_uid', 'create_date', 'write_uid', 'write_date', '__last_update',
                         'message_follower_ids', 'message_partner_ids', 'message_ids', 'website_message_ids']
        child_datas = []
        many_cols = []
        for field in self.fields_get():
            if self[field] and self[field] != False:
                if field == 'child_ids':
                    # data[field] = []
                    for field2 in self[field]:
                        data1 = {}
                        for field1 in field2.fields_get():
                            if field2[field1] and field2[field1] != False:
                                if field1 in UNINCLUDE_COL:
                                    continue
                                if isinstance(field2[field1], str) or isinstance(field2[field1], int) or isinstance(
                                        field2[field1], float) or isinstance(field2[field1], bool):
                                    data1[field1] = field2[field1]
                                else:
                                    data1[field1] = field2[field1].id
                        child_datas.append(data1)
                    continue
                # if fields.type in ('one2many','many2many'):
                #     values = []
                #     for field2 in self[field]:
                #         values.append(field2.id)
                if field in UNINCLUDE_COL:
                    continue

                if isinstance(self[field], str) or isinstance(self[field], int) or isinstance(self[field],
                                                                                              float) or isinstance(
                    self[field], bool):
                    data[field] = self[field]
                else:
                    if self.fields_get()[field]['type'] in ('one2many', 'many2many'):
                        many_cols.append(field)
                    else:
                        data[field] = self[field].id
        id = self.env['res.partner'].create(data)

        for many_col in many_cols:
            id[many_col] = self[many_col]
        if child_datas:
            for child_data in child_datas:
                child_data['parent_id'] = id.id
                self.env['res.partner'].create(child_data)
        self.partner_id = id
        # try:
        self.state = 'done'
        # except Exception as e:
        #     raise UserError(u'转正式客户失败，请在工作流中添加^完成^状态')
        return False
