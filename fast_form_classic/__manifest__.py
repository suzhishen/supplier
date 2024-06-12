# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'WEB FORM EXTEND',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """
        1.调整FORM头部按钮布局，创建/编辑/保存/丢弃
        2.调整【创建】按钮的显示条件  create_condition="[domain]"
        3.调整【编辑】按钮的显示条件  edit_condition="[domain]"
        4.调整【删除】按钮的显示条件  delete_condition="[domain]"
        5.调整【复制】按钮的显示条件  duplicate_condition="[domain]"
        6.调整【归档】按钮的显示条件  archive_condition="[domain]"
    """,
    "category": "Fast/Tools",
    'author': 'fast',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': [
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'fast_form_classic/static/src/xml/*.xml',
            'fast_form_classic/static/src/js/*.js',
            'fast_form_classic/static/src/scss/*.scss',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
