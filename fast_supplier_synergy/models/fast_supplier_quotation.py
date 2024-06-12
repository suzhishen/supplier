# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError, AccessError, UserError

class FastOverallOutsourcingSupplierQuotation(models.Model):
    _name = "fast.overall.outsourcing.supplier.quotation"
    _description = '供应商整体委外价格'
    _rec_name = 'partner_id'
    _order = 'id'

    product_configuration_id = fields.Many2one('fast.blank.configuration', string='款式')
    company_id = fields.Many2one('res.company', string='所属公司')
    # partner_id = fields.Many2one('res.partner', '供应商')
    partner_id = fields.Char('供应商')
    process_price = fields.Float(string='工价', digits='Product Price')
    management_price = fields.Float(string='管理费', digits='Product Price')
    other_price = fields.Float(string='其他费用', digits='Product Price')
    price = fields.Float(string='合计', digits='Product Price')

    bom_price = fields.Float(string='BOM成本', digits='Product Price')
    total_price = fields.Float(string='金额', digits='Product Price')
    remark = fields.Text('备注')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)

    erp_id = fields.Integer(string='ERP端此记录ID')

class FastProductionProcessesSupplierQuotation(models.Model):
    _name = "fast.production.processes.supplier.quotation"
    _description = "供应商工序委外价格"
    _rec_name = 'partner_id'
    _order = 'id'

    product_configuration_id = fields.Many2one('fast.blank.configuration', string='款式')
    company_id = fields.Many2one('res.company', string='所属公司')
    # partner_id = fields.Many2one('res.partner', '供应商', required=1)
    partner_id = fields.Char('供应商')
    mtp_price = fields.Float(string='MTP价格', digits='Product Price')
    other_price = fields.Float(string='其他费用', digits='Product Price')
    price = fields.Float(string='合计', digits='Product Price')
    remark = fields.Text('备注')
    order_line = fields.One2many('fast.production.processes.supplier.quotation.line', 'order_id', string='工序明细')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    erp_id = fields.Integer(string='ERP端此记录ID')

class FastProductionProcessesSupplierQuotationLine(models.Model):
    _name = "fast.production.processes.supplier.quotation.line"
    _description = "MTP价格"
    _rec_name = 'name'
    _order = 'id'

    order_id = fields.Many2one('fast.production.processes.supplier.quotation', string='供应商MTP', ondelete='cascade')
    name = fields.Char('工序', required=1)
    price = fields.Float(string='价格', digits='Product Price', required=1)
    remark = fields.Text('备注')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    erp_id = fields.Integer(string='ERP端此记录ID')