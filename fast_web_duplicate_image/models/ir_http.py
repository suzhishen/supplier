# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        config_parameter = request.env['ir.config_parameter'].sudo()
        result['WEB_COPY_IMAGE_SIZE'] = int(config_parameter.get_param('WEB_COPY_IMAGE_SIZE', 50 * 1204)) ## 100KB
        return result