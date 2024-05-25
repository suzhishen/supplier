from odoo import api, fields, models


class PartnerExtension(models.Model):
    _inherit = 'res.company'

    blank_configuration_ids = fields.Many2many('fast.blank.configuration', relation='fast_blank_configuration_res_company_rel',
                                 column1='company_id', column2='blank_configuration_id', string='所属空白版基础资料')

    erp_supplier_id = fields.Integer('erp供应商ID')

    # company_id = fields.Many2one('res.company', string='所属公司', default=lambda self: self.env.user.company_id.id)