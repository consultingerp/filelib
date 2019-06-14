# Copyright 2019 MuK IT GmbH - Kerrim Abd El-Hamed
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class GeoengineRasterLayer(models.Model):

    _inherit = "geoengine.raster.layer"

    raster_type = fields.Selection(selection_add=[('bing', 'Bing')])
    is_bing = fields.Boolean(compute='_compute_is_bing')
    culture = fields.Char(compute='_compute_culture',store=False)
    bing_imagery_set = fields.Selection([
        ('Road', 'Road'),
        ('RoadOnDemand', 'Road on demand'),
        ('Aerial', 'Aerial'),
        ('AerialWithLabelsOnDemand', 'Aerial With Labels OnDemand'),
        ('Birdseye', 'Birds eye'),
        ('BirdseyeWithLabels', 'Birds eye With Labels'),
        ('Streetside', 'Street side'),
        ('BirdseyeV2', 'Birds eye V2'),
        ('BirdseyeV2WithLabels', 'Birds eye V2 With Labels'),
        ('CanvasDark', 'Canvas Dark'),
        ('CanvasLight', 'Canvas Light'),
        ('CanvasGray', 'Canvas Gray'),
        ('ordnanceSurvey', 'Ordnance Survey')
        ], string="Imagery Set", default="AerialWithLabels")

    bing_key = fields.Char()

    @api.multi
    @api.depends('raster_type')
    def _compute_is_bing(self):
        for rec in self:
            rec.is_bing = rec.raster_type == 'bing'

    @api.multi
    def _compute_culture(self):
        for rec in self:
            if self.env.lang == 'zh_CN':
                rec.culture = 'zh-cN'
            else:
                rec.culture = 'en-us'
