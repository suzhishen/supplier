# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dialog 自定义弹窗大小',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """
        Dialog 自定义弹窗大小
        传入action,action取值如下：
        {
            "extra-modal-max-80": "extra-modal-max-80",
            "extra-modal-max-85": "extra-modal-max-85",
            "extra-modal-max-90": "extra-modal-max-90",
            "extra-modal-max-95": "extra-modal-max-95",
        }
        context = self.env.context.copy()
        context.update({'dialog_size': 'extra-modal-max-95'})
        action['context'] = context
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
            'fast_dialog/static/src/js/*.js',
            'fast_dialog/static/src/js/*.xml',
            'fast_dialog/static/src/css/*.scss',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
