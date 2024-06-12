# -*- coding: utf-8 -*-

import sys
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FastConfigDev(models.Model):
    _name = 'fast.config.dev'
    _description = 'dev地址配置'
    _rec_name = 'url'

    url = fields.Char(string='地址', required=True)
    port = fields.Char(string='端口', required=True)
    is_dev = fields.Boolean(string='是否dev环境')

    @api.model
    def create(self, vals):
        # 检查是否已经存在记录
        if self.search_count([]) >= 2:
            raise ValidationError(_('只允许有测试环境跟线上环境'))
        return super(FastConfigDev, self).create(vals)

    @api.model
    def get_dev_url(self):
        if sys.platform == 'linux':
            record = self.env['fast.config.dev'].sudo().search([('is_dev', '=', True)], limit=1)
        else:
            record = self.env['fast.config.dev'].sudo().search([('is_dev', '=', False)], limit=1)
        if not record:
            raise UserError(_('没有配置dev环境地址'))
        return f'{record.url}:{record.port}'
