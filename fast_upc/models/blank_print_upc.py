from odoo import models,fields,api,_
from odoo.exceptions import UserError


class BlankPrintUpc(models.TransientModel):
    _name = 'blank.print.upc'
    _description = '空白版标签打印'

    product_id = fields.Many2one('product.product', string='空白版')
    type = fields.Selection([('normal', '55*30'), ('single', '30*55'), ('double', '30*55*2')], default='normal', string='标签类型')
    qty = fields.Integer('打印数量', default=1)

    def open_blank_upc_action(self):
        action = self.env.ref('fast_upc.blank_print_upc_wizard_action').sudo().read()[0]
        context = self.env.context
        action['context'] = context
        from_view_id = self.env.ref('fast_upc.blank_print_upc_wizard_form_view')
        action['views'] = [(from_view_id.id, 'form')]
        return action

    def open_blank_upc_action2(self):
        action = self.env.ref('fast_upc.action_blank_print_upc').sudo().read()[0]
        context = self.env.context.copy()
        context['close_footer'] = 1
        action['context'] = context
        return action

    def blank_zpl_print_datas(self, data, type, qty=0):
        upc_tp = False
        print_data = ''
        if type == 'normal':
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_55_30')], limit=1)
        elif type == 'single':
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_30_55')], limit=1)
        elif type == 'double':
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_30_55_2')], limit=1)
        if upc_tp:
            print_data = upc_tp.header_content
            style = data.get('style')
            color = data.get('color')
            size = data.get('size')
            range_qty = int(qty)
            default_code = f'{style}-{color}-{size}'
            product = self.env['product.product'].search([('default_code', '=', default_code)])
            if not product:
                raise UserError(f'空白版款式{default_code}在系统中未找到！')
            for q in range(range_qty):
                print_data += upc_tp.content.format(
                    style_color=f'{style}-{color}',
                    size=size,
                )
        return print_data

    def trigger_widget_click(self):
        print_data = ''
        if not self.product_id:
            raise UserError('空白版不能为空！')
        if not self.type:
            raise UserError('标签模板必须选择！')
        if not self.qty:
            raise UserError('打印数量必须打印零！')
        if self.product_id and self.type and self.qty:
            style = self.product_id.default_code.split('-')[0]
            color = self.product_id.default_code.split('-')[1]
            size = self.product_id.default_code.split('-')[2]
            upc_tp = False
            if self.type == 'normal':
                upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_55_30')], limit=1)
            elif self.type == 'single':
                upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_30_55')], limit=1)
            elif self.type == 'double':
                upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'BLANK_UPC_30_55_2')], limit=1)
            if upc_tp:
                print_data = upc_tp.header_content
                style = style
                color = color
                size = size
                range_qty = int(self.qty)
                for q in range(range_qty):
                    print_data += upc_tp.content.format(
                        style_color=f'{style}-{color}',
                        size=size,
                    )
        return print_data
