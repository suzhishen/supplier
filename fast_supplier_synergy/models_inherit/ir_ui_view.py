from odoo import models,fields,api,_
from odoo.exceptions import UserError


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[
        ('fllow_tree', 'FllowTruee'),
        ('packing_tree', 'PackingTree'),
        ('both_tree', 'both_tree'),
    ])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[
        ('fllow_tree', 'FllowTruee'),
        ('packing_tree', 'PackingTree'),
        ('both_tree', 'both_tree'),
    ], ondelete={
        'fllow_tree': 'cascade',
        'packing_tree': 'cascade',
        'both_tree': 'cascade',
    })

