# Copyright 2019 MuK IT GmbH - Kerrim Abd El-Hamed
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)


class GeoengineRasterLayer(models.Model):

    _inherit = "geoengine.raster.layer"

    raster_type = fields.Selection(selection_add=[
        ('bing', _('Bing')), ('baidu', _('Baidu')), ('amap', _('aMap')),
        ('google_cn', _('Google CN'))], default='bing')
    # is_bing = fields.Boolean(compute='_compute_is_bing')
    # is_baidu = fields.Boolean(compute='_compute_is_baidu')
    # is_amap = fields.Boolean(compute='_compute_is_amap')
    # is_google_cn = fields.Boolean(compute='_compute_is_google_cn')
    culture = fields.Char(compute='_compute_culture', store=False)
    bing_imagery_set = fields.Selection([
        ('Road', 'Road'),
        ('RoadOnDemand', 'Road on demand'),
        ('Aerial', 'Aerial'),
        ('AerialWithLabels', 'Aerial With Labels'),
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
        ], string="Imagery Set", default="CanvasLight")
    baidu_imagery_set = fields.Selection([
        ('baidu-source', _('百度行政区划')),
        ('baidu-sourcelabel', _('百度地图标注')),
        ('baidu-sourceraster', _('百度地图影像'))
    ], string="Imagery Set", default="baidu-sourcelabel")
    amap_imagery_set = fields.Selection([
        ('aMap-img', _('影像底图')),
        ('aMap-vec', _('街道底图')),
        ('aMap-roadLabel', _('路网+标注'))
        ], string="Imagery Set", default="aMap-roadLabel")
    google_cn_imagery_set = fields.Selection([
        ('google-img', _('影像')),
        ('google-vec', _('街道'))
        ], string="Imagery Set", default="google-vec")
    bing_key = fields.Char(default='AqY4IFeQhJPHi5FjGBNc7hfgUNcaVf7S_qyyP_dlVCesSJUqI7dBA-gsyoAIUvGu')
    baidu_key = fields.Char()

    # @api.multi
    # @api.depends('raster_type')
    # def _compute_is_bing(self):
    #     for rec in self:
    #         rec.is_bing = rec.raster_type == 'bing'
    #
    # @api.multi
    # @api.depends('raster_type')
    # def _compute_is_baidu(self):
    #     for rec in self:
    #         rec.is_baidu = rec.raster_type == 'baidu'
    #
    # @api.multi
    # @api.depends('raster_type')
    # def _compute_is_amap(self):
    #     for rec in self:
    #         rec.is_bing = rec.raster_type == 'amap'
    #
    # @api.multi
    # @api.depends('raster_type')
    # def _compute_is_google_cn(self):
    #     for rec in self:
    #         rec.is_baidu = rec.raster_type == 'google_cn'

    @api.multi
    def _compute_culture(self):
        lang = self.env.lang if self.env.lang else self.env.user.lang
        for rec in self:
            rec.culture = lang


    # @api.multi
    # def _compute_culture(self):
    #     lang = self.env.lang if self.env.lang else self.env.user.lang
    #     for rec in self:
    #         if lang == 'zh_CN':
    #             rec.culture = 'zh-cn'
    #         else:
    #             rec.culture = 'en-us'

