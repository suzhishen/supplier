# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '数据模板下载',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """""",
    "category": "Fast/Tools",
    'author': 'fast',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fast_data_product_template_download_views.xml',
        'views/menus_views.xml'
    ],
    'assets': {
        'web.assets_backend': [

        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
