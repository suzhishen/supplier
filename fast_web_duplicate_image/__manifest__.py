# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '限制图片上传大小',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'summary': """""",
    'description': """
        通过在config_parameter.get_param('WEB_COPY_IMAGE_SIZE', 100 * 1204) ## 100KB  限制文件大小，默认100KB
        复制图片上传:"可以直接截图,也可以复制图片"
        <field name="image_1920" widget="web_copy_image"/>
    """,
    "category": "Fast/Fast",
    'author': 'fast',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': [
        'web','base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fast_web_duplicate_image/static/src/js/image_field.js'
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
