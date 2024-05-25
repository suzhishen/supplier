from odoo import models,fields,api,_
from odoo.exceptions import UserError


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[
        ('fllow_tree', 'FllowTruee'),
        ('variance_report_tree', 'VarianceReportTree')
    ])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[
        ('fllow_tree', 'FllowTruee'),
        ('variance_report_tree', 'VarianceReportTree'),
    ], ondelete={
        'fllow_tree': 'cascade',
        'variance_report_tree': 'cascade',
    })

