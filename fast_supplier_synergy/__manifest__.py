{
    'name': '供应商协同端',
    'version': '16.0',
    'sequence': 1,
    'category': 'Fast/Fast',
    'summary': """""",
    'description': """""",
    'author': 'fast',
    'price': '',
    'currency': '',
    'website': '',
    'support': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/supplier_security.xml',
        'data/blank_packing_list_detail_data.xml',
        'views/fast_blank_configuration_views.xml',
        'views/fast_blank_bom_views.xml',
        'views/fast_supplier_order_blank_views.xml',
        'views/fast_outsource_order_blank_line_fllow_views.xml',
        'views/ir_actions_client_views.xml',
        'views/fast_blank_packing_list_views.xml',
        'views/report_forms_views.xml',
        'views/menu_views.xml',
        # 'views/fast_create_material_requirements_wizard_views_apply_material.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # layui组件
            'fast_supplier_synergy/static/src/layui/layui.js',
            # 订单跟进Tree
            'fast_supplier_synergy/static/src/js/fllow_tree/*.js',
            'fast_supplier_synergy/static/src/js/fllow_tree/*.xml',
            'fast_supplier_synergy/static/src/js/fllow_tree/*.scss',
            # 订单中心-订单明细
            'fast_supplier_synergy/static/src/js/outsourced_order_show_tree/*.js',
            'fast_supplier_synergy/static/src/js/outsourced_order_show_tree/*.xml',
            'fast_supplier_synergy/static/src/js/outsourced_order_show_tree/*.scss',
            # 订单中心-变更明细
            'fast_supplier_synergy/static/src/js/change_order_show_tree/*.js',
            'fast_supplier_synergy/static/src/js/change_order_show_tree/*.xml',
            'fast_supplier_synergy/static/src/js/change_order_show_tree/*.scss',
            # 打印装箱单 LABEL
            'fast_supplier_synergy/static/src/js/print_product_blank_clp_button/*.js',
            'fast_supplier_synergy/static/src/js/print_product_blank_clp_button/*.xml',
            # 空白版装箱单 BUTTON
            'fast_supplier_synergy/static/src/js/bank_clp_button/*.js',
            'fast_supplier_synergy/static/src/js/bank_clp_button/*.xml',
            # 差异报表
            'fast_supplier_synergy/static/src/js/report_forms/*.js',
            'fast_supplier_synergy/static/src/js/report_forms/*.xml',
            'fast_supplier_synergy/static/src/js/report_forms/*.scss',
        ],
        'web.assets_common': [
            'fast_supplier_synergy/static/src/css/*.css',
            'fast_supplier_synergy/static/src/layui/css/layui.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
}
