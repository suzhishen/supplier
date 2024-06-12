# -*- coding: utf-8 -*-
{
    'name': "supplier_users",

    'summary': """供应商用户管理""",

    'description': """
    用于管理用户多公司多用户
    """,

    "license": "LGPL-3",
    'author': "fast",
    'website': "https://www.yourcompany.com",
    'category': 'fast/fast',
    'version': '16.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/supplier_users_security.xml',
        'views/supplier_users_views.xml',
        'wizard/supplier_change_password_view.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
}
