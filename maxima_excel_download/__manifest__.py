# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'One2many Excel Download',
    'version': "16.0.1.0.0",
    'summary': """One2many Excel Download""",
    'description': """
        <xpath expr="//field[@name='order_line']" position="attributes">
            <attribute name="excel_download">1</attribute>
        </xpath>
        或
        <field name="order_line" excel_download="1">
            <tree>...</tree>
        </field>
    """,
    'category': 'Maxima/tools',
    'author': 'Roy',
    'price': '',
    'currency': '',
    "license": "LGPL-3",
    'depends': ['web', 'base'],
    'data': [
        'security/ir.model.access.csv', ],

    'assets': {
        'web.assets_backend': [
            'maxima_excel_download/static/src/xml/*.xml',
            'maxima_excel_download/static/src/js/X2ManyField.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
