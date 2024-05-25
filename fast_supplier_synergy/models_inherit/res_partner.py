from odoo import api, fields, models


class PartnerExtension(models.Model):
    _inherit = 'res.partner'

    blank_configuration_ids = fields.Many2many('fast.blank.configuration', relation='fast_blank_configuration_res_partnere_rel',
                                 column1='partner_id', column2='blank_configuration_id', string='所属空白版基础资料')
    erp_partner_id = fields.Integer('erp供应商ID')
