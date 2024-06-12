###################################################################################
#
#    Copyright (c) 2017-today MuK IT GmbH.
#
#    This file is part of MuK Backend Theme
#    (see https://mukit.at).
#
#    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
###################################################################################

from odoo import models, fields, api


class ResUsers(models.Model):
    
    _inherit = 'res.users'
    
    #----------------------------------------------------------
    # Properties
    #----------------------------------------------------------
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'sidebar_type',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            'sidebar_type',
        ]

    #----------------------------------------------------------
    # Fields
    #----------------------------------------------------------
    
    sidebar_type = fields.Selection(
        selection=[
            ('invisible', '隐藏'),
            ('small', '小图标'),
            ('large', '大图标')
        ], 
        string="侧边栏菜单显示类型",
        default='large',
        required=True,
    )
