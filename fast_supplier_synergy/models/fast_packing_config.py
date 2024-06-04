# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FastPackingConfig(models.Model):
    _name = 'fast.packing_follow.config'
    _description = '装箱配置'
    _rec_name = 'number'

    number = fields.Char(string='件数', required=True)
    percentage = fields.Char(string='限制最大超出百分比（%）', required=True)
    limit_out_qty = fields.Integer(string='限制超出件数（件）', compute='_compute_limit_out_qty', store=True)

    @api.depends('number', 'percentage')
    def _compute_limit_out_qty(self):
        for record in self:
            record.limit_out_qty = int(record.number) * (int(record.percentage) / 100)

