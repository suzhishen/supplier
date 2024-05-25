from odoo import models,fields,api,_
from odoo.exceptions import UserError


class ResGroups(models.Model):
    _inherit = 'res.groups'

    group_type = fields.Selection([('system', '系统'), ('custom', '自定义')], default='system', string='类型')