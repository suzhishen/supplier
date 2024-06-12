# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'TREE NO',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """
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
            'fast_tree_rowno/static/src/xml/*.xml',
            'fast_tree_rowno/static/src/js/*.js',
            'fast_tree_rowno/static/src/scss/*.scss',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
