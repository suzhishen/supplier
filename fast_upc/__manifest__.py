# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'UPC模板管理',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': "",
    "category": "Leda/Leda",
    'author': 'Leda',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': [
        'base', 'web'
    ],
    'data': [
        'data/upc_template_view.xml',
        'data/upc_blank_upc_template_view.xml',
        'data/res_groups_view.xml',
        # 'data/cpcl_template_view.xml',
        'data/clp_upc_template_view.xml',
        'data/cpcl_template_basic_view.xml',
        'data/cpcl_template_blank_view.xml',
        'data/cpcl_template_blank_out_view.xml',
        'security/ir.model.access.csv',
        'views/zebra_upc_template_view.xml',
        'views/printer_cpcl_template_view.xml',
        # client定义
        'views/zebra_print_client_view.xml',

        'wizard/blank_print_upc_wizard_view.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [

            # 斑马浏览器打印包
            'fast_upc/static/src/js/lib/BrowserPrint-3.1.250.min.js',
            'fast_upc/static/src/js/lib/BrowserPrint-Zebra-1.1.250.min.js',

            # 空白版打印
            'fast_upc/static/src/js/blank_barcode/*.js',
            'fast_upc/static/src/js/blank_barcode/*.scss',
            'fast_upc/static/src/js/blank_barcode/*.xml',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
