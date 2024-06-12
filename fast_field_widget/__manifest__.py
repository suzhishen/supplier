# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Fields EXTEND',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """
        Float字段Widget 例如：[5.23 kg]
        <field name="product_uom_qty" widget="uom_float" options="{'uomField':'uom_id'}"/>
        Interage 字段Widget 例如：[5 kg]
        <field name="product_uom_qty" widget="uom_int" options="{'uomField':'uom_id'}"/>
        金额 / 单位 例如：[￥5 / kg]
        <field name="product_uom_qty" widget="monetary_uom" options="{'uomField':'uom_id', 'monetaryField': 'currency_id'}"/>
    """,
    "category": "Fast/Fast",
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
            'fast_field_widget/static/src/js/monetary_field.js',
            'fast_field_widget/static/src/js/field_Float_uom.js',
            'fast_field_widget/static/src/js/field_Interage_uom.js',
            'fast_field_widget/static/src/js/field_float_monetary_uom.js',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
