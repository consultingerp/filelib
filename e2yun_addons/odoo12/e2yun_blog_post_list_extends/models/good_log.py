# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import random
from odoo.modules.module import get_module_resource
from urllib.request import urlretrieve
import base64
import os
from PIL import Image

class GoodLog(models.Model):
    _name = 'good.log'

    blog_post_id = fields.Many2one('blog.post',string='Blog Post')
    user_id = fields.Many2one('res.users',string='User')


