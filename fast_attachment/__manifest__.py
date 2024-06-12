# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '文件',
    'version': '16.0.1.0.0',
    'sequence': 2,
    'summary': """""",
    'description': "",
    "category": "Fast/Tools",
    'author': 'fast',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': [
        'base', 'web'
    ],
    'data': [
        'data/res_groups_view.xml',
        'data/ir_attachment_category_data.xml',
        'security/ir.model.access.csv',
        'views/ir_attachment_category_views.xml',
        'views/ir_attachment_views.xml',
        'views/menu_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'fast_attachment/static/src/views/fast_attachment_kanban/*.js',
            'fast_attachment/static/src/views/fast_attachment_kanban/*.xml',
            'fast_attachment/static/src/views/fast_attachment_kanban/*.css',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
