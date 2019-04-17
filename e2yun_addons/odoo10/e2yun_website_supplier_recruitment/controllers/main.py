# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.website.models.website import slug
from odoo.http import request


# NB: DO NOT FORWARD PORT THE FALSY LEAVES IN 11.0
class WebsiteSupplierRecruitment(http.Controller):
    @http.route([
        '/supplierjobs',
        '''/supplierjobs/country/<model("res.country", "[(0, '=', 1)]"):country>''',
        '''/supplierjobs/product/<model("product.template", "[(0, '=', 1)]"):product>''',
        '''/supplierjobs/country/<model("res.country"):country>/product/<model("product.template", "[(0, '=', 1)]"):product>''',
        '/supplierjobs/office/<int:office_id>',
        '''/supplierjobs/country/<model("res.country", "[(0, '=', 1)]"):country>/office/<int:office_id>''',
        '''/supplierjobs/product/<model("product.template", "[(0, '=', 1)]"):product>/office/<int:office_id>''',
        '''/supplierjobs/country/<model("res.country"):country>/product/<model("product.template", "[(0, '=', 1)]"):product>/office/<int:office_id>''',
    ], type='http', auth="public", website=True)
    def jobs(self, country=None, product=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        Jobs = env['supplier.job']

        # List jobs available to current UID
        job_ids = Jobs.search([], order="website_published desc,no_of_recruitment desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)

        # Default search by user country
        if not (country or product or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce products and countries offices of those jobs
        products = set(j.product_id for j in jobs if j.product_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if product:
            jobs = (j for j in jobs if j.product_id and j.product_id.id == product.id)
        if office_id and office_id in map(lambda x: x.id, offices):
            jobs = (j for j in jobs if j.address_id and j.address_id.id == office_id)
        else:
            office_id = False

        # Render page
        return request.render("e2yun_website_supplier_recruitment.index", {
            'jobs': jobs,
            'countries': countries,
            'products': products,
            'offices': offices,
            'country_id': country,
            'product_id': product,
            'office_id': office_id,
        })

    @http.route('/supplierjobs/add', type='http', auth="user", website=True)
    def jobs_add(self, **kwargs):
        # avoid branding of website_description by setting rendering_bundle in context
        job = request.env['supplier.job'].with_context(rendering_bundle=True).create({
            'name': _('Job Title'),
        })
        return request.redirect("/supplierjobs/detail/%s?enable_editor=1" % slug(job))

    @http.route('/supplierjobs/detail/<model("supplier.job"):job>', type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):
        return request.render("e2yun_website_supplier_recruitment.detail", {
            'job': job,
            'main_object': job,
        })

    @http.route('/supplierjobs/apply/<model("supplier.job"):job>', type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        error = {}
        default = {}
        if 'e2yun_website_supplier_recruitment_error' in request.session:
            error = request.session.pop('e2yun_website_supplier_recruitment_error')
            default = request.session.pop('e2yun_website_supplier_recruitment_default')
        return request.render("e2yun_website_supplier_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
        })
