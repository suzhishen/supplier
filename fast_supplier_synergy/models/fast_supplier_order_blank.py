# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

BlankSize = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t', '4', '5', '6', '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']

import requests
from odoo.exceptions import UserError, ValidationError
Dev_url = 'http://192.168.6.50:10010'


class FastSupplierOrderBlank(models.Model):
    _name = 'fast.supplier.order.blank'
    _description = '供应商空白版订单'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    erp_id = fields.Integer('erp_id')
    name = fields.Char('订单号', copy=False, required=1, help='po号')
    type = fields.Selection([('A', 'FOB'), ('B', 'MTP')], copy=False, string='加工类型')
    processing_plant = fields.Char('加工厂')
    user_name = fields.Char('跟单员')
    order_quantity = fields.Integer('订单数量')
    completed_quantity = fields.Integer('已完成数量')
    unfinished_quantity = fields.Integer('待完成数量')
    date_planned = fields.Char('要求交期')
    # date_expected = fields.Date('预计交期')
    state = fields.Selection([('draft', '待完成'), ('part', '部分完成'), ('done', '已完成'), ('cancel', '已取消')],
                             string='状态', default='draft', copy=True)
    partner_price_line = fields.One2many('fast.process_cost', 'blank_order_id', string='相关费用', index=True)
    blank_order_detail_line = fields.One2many('fast.blank_order_detail', 'blank_order_id', string='相关明细', index=True)
    main_material_order_line = fields.One2many('fast.blank.order.material.requirements', 'outsource_order_blank_id',
                                               string='相关物料需求(主料)', domain=[('conf_type', '=', 'main')])
    sub_material_order_line = fields.One2many('fast.blank.order.material.requirements', 'outsource_order_blank_id',
                                              string='相关物料需求(辅料)', domain=[('conf_type', '=', 'sub')])
    confirm_state = fields.Selection([('not_confirm', '未接收'), ('have_confirm', '已接收')], string='确认接收状态', default='not_confirm')
    change_state = fields.Selection([('not_change', '无需变更'), ('await_change', '待变更明细'), ('have_change', '已变更明细')], string='变更状态', default='not_change')
    state = fields.Selection([('draft', '待完成'), ('part', '部分完成'), ('done', '已完成'), ('cancel', '已取消')], default='draft', string='状态')

    # @api.constrains('date_expected')
    # def _sync_erp_date_expected(self):
    #     """
    #     同步erp预计交期
    #     :return:
    #     """
    #     values = {
    #         'params': {
    #             'po': self.name,
    #             'date_expected': self.date_expected.strftime('%Y-%m-%d'),
    #         }
    #     }
    #     headers = {'Content-Type': 'application/json'}
    #     response = requests.post(url=f'{Dev_url}/leda/reply_delivery', json=values, headers=headers)
    #     result = response.json().get('result', False)
    #     if not (result and result.get('code', False) and result.get('code', False) == 200):
    #         raise UserError(response.text)

    def confirm_packing(self):
        """
        订单中心 - 确认接收
        :return:
        """
        self.confirm_state = 'have_confirm'

        # detail_ids = []
        # for item in self.blank_order_detail_line:
        #     if item.order_quantity > 0:
        #         detail_ids.append(item.id)
        # blank_order_detail = self.blank_order_detail_line.search([('id', 'in', detail_ids)])
        # product_color_name_list = blank_order_detail.jsonify(['product_color_name', 'date_expected'])
        # product_color_name_list = [dict(t) for t in {tuple(d.items()) for d in product_color_name_list}]
        # date_expected_list = list(set(blank_order_detail.mapped('date_expected')))
        # for date_expected in date_expected_list:
        #     if not date_expected:
        #         raise UserError('请填写订单明细所有的预计交期')
        # self.confirm_state = 'have_confirm'
        # # 同步erp预计交期
        # values = {
        #     'params': {
        #         'po': self.name,
        #         'product_color_name_list': product_color_name_list,
        #     }
        # }
        # headers = {'Content-Type': 'application/json'}
        # response = requests.post(url=f'{Dev_url}/leda/reply_delivery', json=values, headers=headers)
        # result = response.json().get('result', False)
        # if not (result and result.get('code', False) and result.get('code', False) == 200):
        #     raise UserError(response.text)

    def get_outsourced_order_show_datas(self):
        """
        订单中心 - 订单明细
        :return:
        """
        foot_total = sum(self.blank_order_detail_line.mapped('order_quantity'))
        foot_total_done_qty = sum(self.blank_order_detail_line.mapped('completed_quantity'))
        foot_total_un_done_qty = sum(self.blank_order_detail_line.mapped('unfinished_quantity'))
        datas = []
        name_list = list(set(self.blank_order_detail_line.mapped('name')))
        for name in name_list:
            now_record_detail = self.env['fast.blank_order_detail'].search(
                [('blank_order_id', '=', self.id), ('name', '=', name)])
            detail_total = sum(now_record_detail.mapped('order_quantity'))
            detail_total_done_qty = sum(now_record_detail.mapped('completed_quantity'))
            detail_total_un_done_qty = sum(now_record_detail.mapped('unfinished_quantity'))
            # 款号 + 总款数
            kh_value = {
                'origin_name': name,
                'origin_total': detail_total,
                'origin_total_done_qty': detail_total_done_qty,
                'origin_total_un_done_qty': detail_total_un_done_qty,
                'product_template_datas': [],
            }
            color_list = list(set(now_record_detail.mapped('product_color_name')))
            for color in color_list:
                now_detail_color_ids = now_record_detail.filtered(lambda record: record.product_color_name == color)
                color_total = sum(now_detail_color_ids.mapped('order_quantity'))
                color_total_done_qty = sum(now_detail_color_ids.mapped('completed_quantity'))
                color_total_un_done_qty = sum(now_detail_color_ids.mapped('unfinished_quantity'))
                # 颜色 + 款色总数
                ys_value = {
                    'color_name': color.split('-')[-1],
                    'product_tmpl_total': color_total,
                    'product_tmpl_done_qty': color_total_done_qty,
                    'product_tmpl_un_done_qty': color_total_un_done_qty,
                    'date_expected': now_detail_color_ids[0].date_expected,
                    'product_datas': [],
                }

                size_list = list(set(now_detail_color_ids.mapped('product_name')))
                for size in size_list:
                    now_detail_size_id = now_detail_color_ids.filtered(lambda record: record.product_name == size)
                    # 需求（订单数:已交付数:未交付数）
                    szie_value = {
                        'size_name': size.split('-')[-1],
                        'product_qty': now_detail_size_id.order_quantity,
                        'done_qty': now_detail_size_id.completed_quantity,
                        'un_done_qty': now_detail_size_id.unfinished_quantity
                    }
                    ys_value['product_datas'].append(szie_value)
                kh_value['product_template_datas'].append(ys_value)
            datas.append(kh_value)

        # 尺寸排序
        for item in datas:
            for product_template_data in item['product_template_datas']:
                product_template_data['product_datas'] = sorted(product_template_data['product_datas'],
                                                                key=lambda x: BlankSize.index(x['size_name'].lower()))
        return {
            'state': self.state,
            'datas': datas,
            # 底部统计总数
            'foot_total': foot_total,
            'foot_total_done_qty': foot_total_done_qty,
            'foot_total_un_done_qty': foot_total_un_done_qty
        }

    def get_change_order_show_datas(self):
        """
        订单中心 - 变更明细
        :return:
        """
        datas = []
        name_list = list(set(self.blank_order_detail_line.mapped('name')))
        for name in name_list:
            now_record_detail = self.env['fast.blank_order_detail'].search(
                [('blank_order_id', '=', self.id), ('name', '=', name), ('change_quantity', '!=', False)])
            # 款号 + 总款数
            kh_value = {
                'origin_name': name,
                'product_template_datas': [],
            }
            color_list = list(set(now_record_detail.mapped('product_color_name')))
            for color in color_list:
                now_detail_color_ids = now_record_detail.filtered(lambda record: record.product_color_name == color)
                # 颜色
                ys_value = {
                    'color_name': color.split('-')[-1],
                    'product_datas': [],
                }

                size_list = list(set(now_detail_color_ids.mapped('product_name')))
                for size in size_list:
                    now_detail_size_id = now_detail_color_ids.filtered(lambda record: record.product_name == size)
                    # 需求（订单数:已交付数:未交付数）
                    szie_value = {
                        'size_name': size.split('-')[-1],
                        'change_quantity': now_detail_size_id.change_quantity,
                    }
                    ys_value['product_datas'].append(szie_value)
                kh_value['product_template_datas'].append(ys_value)
            datas.append(kh_value)

        # 尺寸排序
        for item in datas:
            for product_template_data in item['product_template_datas']:
                product_template_data['product_datas'] = sorted(product_template_data['product_datas'],
                                                                key=lambda x: BlankSize.index(x['size_name'].lower()))
        return {
            'state': self.state,
            'datas': datas,
        }


class BlankOrderDetail(models.Model):
    _name = 'fast.blank_order_detail'
    _description = '订单明细'


    blank_order_id = fields.Many2one('fast.supplier.order.blank', string='所属订单', ondelete='cascade')
    packing_list_detail_quantity = fields.One2many('fast.blank.packing_list_detail', 'blank_order_detail_id', string='相关装箱单明细', index=True)

    name = fields.Char(string='款号', help='空白版款号')
    po_name = fields.Char(related='blank_order_id.name', string='订单号', store=True, help='po号')
    processing_plant = fields.Char(related='blank_order_id.processing_plant', string='加工厂', store=True)
    product_color_name = fields.Char(string='颜色')
    product_name = fields.Char(string='产品')
    order_quantity = fields.Integer('订单数量')
    completed_quantity = fields.Integer('已完成数量', compute='_compute_completed_quantity', store=True)
    unfinished_quantity = fields.Integer('待完成数量', compute='_compute_completed_quantity', store=True)
    # stored_quantity = fields.Char('供应商录入数量')
    confirm_state = fields.Selection(related='blank_order_id.confirm_state', string='确认接收状态', store=True)
    date_planned = fields.Char('要求交期')
    date_expected = fields.Char('预计交期')
    change_quantity = fields.Char('变更数量')

    # 后加
    order_date = fields.Char(string='下单日期')
    material_state = fields.Char('发料状态')
    style_name = fields.Char('款式名称')
    order_type = fields.Char('订单类型')
    order_state = fields.Char('订单状态')

    @api.depends('packing_list_detail_quantity.received_quantity', 'packing_list_detail_quantity.receive_state', 'packing_list_detail_quantity.difference_quantity')
    def _compute_completed_quantity(self):
        for record in self:
            record.completed_quantity = sum(record.packing_list_detail_quantity.mapped('received_quantity'))
            record.unfinished_quantity = record.order_quantity - record.completed_quantity

    @api.model
    def update_date_expected(self, args, **kwargs):
        # 同步erp预计交期
        po = kwargs.get('po')
        records = self.search([('product_color_name', '=', kwargs.get('product_color_name'))])
        records.write({'date_expected': kwargs.get('date_expected')})
        product_color_name_list = records.jsonify(['product_color_name', 'date_expected'])
        values = {
            'params': {
                'po': po,
                'product_color_name_list': product_color_name_list,
            }
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=f'{Dev_url}/leda/reply_delivery', json=values, headers=headers)
        result = response.json().get('result', False)
        if not (result and result.get('code', False) and result.get('code', False) == 200):
            raise UserError(response.text)
        print('update_date_expected')
        print(kwargs)

    @api.model
    def change_update_order_detail(self, args, **kwargs):
        # 订单变更明细更新
        records = self.search([('product_color_name', '=', kwargs.get('product_color_name'))], order='id asc')
        for item in records:
            if item.change_quantity and item.change_quantity[0] == '-':
                item.order_quantity -= int(item.change_quantity[1:])
                item.unfinished_quantity -= int(item.change_quantity[1:])
            elif item.change_quantity and item.change_quantity[0] == '+':
                item.order_quantity += int(item.change_quantity[1:])
                item.unfinished_quantity += int(item.change_quantity[1:])
            item.change_quantity = False
        print('change_update_order_detail')
        print(kwargs)


    # todo ------------ 订单跟进 ------------
    #
    def btn_download_data_excel(self, download_datas):
        """
        订单跟进下载excel
        :return:
        """
        print('订单跟进下载excel')
        try:
            size_list = list(set([size['size_name'] for order_line in (x['order_line'] for x in download_datas) for size in order_line]))
            size_list = sorted(size_list, key=lambda size: BlankSize.index(size.lower()))
            headers = ['#', '下单日期', '工厂', 'PO#', '款号', '款色', '领料状态', '总需求数', '总入仓数',
                       '总欠数'] + size_list + ['要求交期', '预计交期', '外发类型', '款式名称', 'SC', '跟单员', '订单类型']
            row_datas = []
            seq = 1
            for line in download_datas:
                order_line = line['order_line']  # 需求明细
                order_line_datas = []
                for size in size_list:
                    order_qty = [x['product_qty'] for x in order_line if x['size_name'] == size]
                    order_qty = '' if not order_qty else order_qty[0]
                    order_line_datas.append(order_qty)
                line_data = [seq, line['create_date'], line['partner_name'], line['po'], line['product_configuration_code'], line['product_tmpl_code'], '领料状态', line['order_line_total'], line['incoming_line_total'], line['incomplete_line_total']]
                line_data += order_line_datas + [line['date_planned'] or '', line['date_expected'] or '', line['order_type'], line['product_configuration_name'], line['blank_order_type']]
                seq += 1
                row_datas.append(line_data)
            return self.env['fast.data.product.template.download'].__get_or_create_work_book_xlsx_datas__('空白版订单跟进.xlsx', headers, row_datas)
        except Exception as error:
            raise UserError(error)

    # 获取页面条数/分页
    @api.model
    def get_fllow_tree_count(self, domain=[], page_groupby=[]):
        """
        订单跟进右上角 条数/分页
        :return:
        """
        grouped_data = self.env['fast.blank_order_detail'].read_group(
            domain=[('confirm_state', '=', 'have_confirm')],
            fields=['product_color_name'],
            groupby=['product_color_name'],
            orderby=False,
        )
        return len(grouped_data)

    # 获取列表数据
    @api.model
    def get_fllow_tree_render_view_datas(self, domain=[], limit=80, offset=0, page_groupby=[], front_context={}):
        """
        订单跟进界面数据
        :return:
        """
        grouped_data = self.env['fast.blank_order_detail'].search([], order='blank_order_id desc').read_group(
            domain=[('confirm_state', '=', 'have_confirm')],
            limit=limit,
            offset=offset,
            fields=list(self._fields.keys()),
            groupby='product_color_name'
        )
        # 获取每个组的完整记录信息
        full_records = {}
        for group in grouped_data:
            if not group.get('__domain'):
                continue
            records = self.search_read(domain=group['__domain'], fields=list(self._fields.keys()))
            full_records.update({
                group['product_color_name']: records
            })
        datas = []

        foot_order_line_total = foot_incoming_line_total = foot_incomplete_line_total = 0
        for index, item in enumerate(full_records.values()):
            value = {
                'create_date': '下单日期',  # 下单日期
                'partner_name': item[0].get('processing_plant', ''),  # 加工厂
                'po': item[0].get('name', ''),  # PO#
                'product_tmpl_code': item[0]['product_color_name'],  # 款色
                'product_configuration_name': '款式名称',  # 款式名称
                'date_planned': item[0].get('date_planned') or '',  # 要求交期
                'order_type': 'FOB' if item[0].get('type', '') else 'MTP',  # 外发类型
                'product_configuration_code': item[0].get('name', ''),  # 款号
                'date_expected': item[0].get('date_expected') if item[0].get('date_expected') and item[0].get('date_expected') != 'false' else '',  # 预计交期
                'incomplete_line': [],  # 欠数明细
                'blank_order_type': '订单类型',  # 订单类型
            }

            order_line_total = 0
            incoming_line_total = 0
            incomplete_line_total = 0
            for line in item:
                size_name = line['product_name'].split('-')[-1]
                packing_list_detail = self.env['fast.blank.packing_list_detail'].search([('id', 'in', line['packing_list_detail_quantity'])])
                incomplete_line = {
                    'size_name': size_name,
                    'product_qty': str(line['order_quantity'] - line['completed_quantity']),
                    'have_packed_qty': sum(packing_list_detail.mapped('quantity')),     # 已装箱明细
                }
                value['incomplete_line'].append(incomplete_line)

                order_line_total += line['order_quantity']  # 款色总需求数
                incoming_line_total += line['completed_quantity']  # 款色总入仓数
                incomplete_line_total += line['unfinished_quantity']  # 款色总欠数
            foot_order_line_total += order_line_total  # 总需求数
            foot_incoming_line_total += incoming_line_total  # 总入仓数
            foot_incomplete_line_total += incomplete_line_total  # 总欠数

            value.update({
                'order_line_total': order_line_total,  # 款色总需求数
                'incoming_line_total': incoming_line_total,  # 款色总入仓数
                'incomplete_line_total': incomplete_line_total,  # 款色总欠数
            })
            datas.append(value)
        return {
            'result': datas,
            'foot_order_line_total': foot_order_line_total,
            'foot_incoming_line_total': foot_incoming_line_total,
            'foot_incomplete_line_total': foot_incomplete_line_total,
        }

    @api.model
    def action_open_fast_order_center_follow_tree_blank_in_client(self, args, **kwargs):
        """
        订单跟进 - 总入仓数 查看详情
        :return:
        """
        print('123')
        po_style_data = kwargs.get('po_style_data', False)
        action = self.env.ref('fast_supplier_synergy.fast_order_center_follow_tree_blank_in_client').sudo().read()[0]
        context = self.env.context.copy()
        sizes = []
        for item in po_style_data.get('incomplete_line', []):
            sizes.append(item['size_name'])
        record = {
            'sizes': sizes,  # 尺码
            'po': 'po',  # PO#
            'product_tmpl_code': 'M30050-PNK',  # 款号
            'order_data': [126, 262, 327, 194, 160, 60],  # 订单细码数
            'order_line_total': 1129,  # 订单总数
            'in_move_datas': [{'date': '2024-04-28', 'move_line_datas': [19.0, 50.0, 137.0, 0, 0, 0], 'qty': 206.0, 'move_line_ids': [276595, 276616, 276665, 278310, 276663]}],  # 入仓细码数（按日期）
            'in_move_datas_summary': [19.0, 50.0, 137.0, 0, 0, 0],  # 总入仓细码数（所有）
            'in_move_datas_summary_total': 206,  # 入库总数=已入库数 - 已退货数
            'out_move_datas': [],  # 退货细码数（按日期）
            'out_move_datas_summary':  [0, 0, 0, 0, 0, 0],  # 退货细码数（所有）
            'out_move_datas_summary_total': 0,  # 退货总数
            'unfinished_datas': [107, 212, 190, 194, 160, 60],  # 未完成细码数
            'unfinished_qty':  923,  # 未完成总数 = 订单数量 - 入库数量
            'diff_datas': [107, 212, 190, 194, 160, 60],  # 差异数量
            'diff_qty': 923,  # 差异总数
        }
        context.update({
            'dialog_size': 'large',
            'close_footer': True,
            'record': record
        })
        action['context'] = context
        action['target'] = 'new'
        return action

    """获取款色BOM物料（主料+辅料）用量明细"""
    def get_blank_order_bom_detail(self,*args,**kwargs):
        values = {'params':{}}
        values['params']['datas'] = {
            'po':kwargs.get('po',''),
            'partner_name':kwargs.get('partner_name',''),
            'product_tmpl_code':kwargs.get('product_tmpl_code',''),
            'product_configuration_code':kwargs.get('product_configuration_code',''),
        }
        Dev_url = 'http://192.168.6.50:10010'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=f'{Dev_url}/leda/blank_order_material_bom_detail', json=values, headers=headers)
        import json
        if response.status_code == 200:
            data = json.loads(response.text)
            result = data['result']
            print(data)
            wizard_id = self.env['fast.create.material.requirements.wizard'].sudo().create({
                # 'outsource_order_blank_id': self.id,
                # 'outsource_order_blank_line_ids': [(6, 0, product_tmpl_lines.ids)],
                'default_code': 'fasfdsa',
                'erp_id':result['data']['erp_id']
            })
            for line in result['data']['order_line']:
                self.env['fast.create.material.requirements.wizard.line'].create({
                    'order_qty': line['order_qty'],
                    'product_id': line['product_id'],
                    'product_default_code':  line['product_default_code'],
                    'product_default_name':  line['product_default_name'],
                    'color_cn_name':  line['color_cn_name'],
                    'product_spec_remark':  line['product_spec_remark'],
                    'conf_type':line['conf_type'],
                    'os_assist_product_qty': line['os_assist_product_qty'],
                    'assist_product_qty': line['assist_product_qty'],
                    'bom_need_qty': line['bom_need_qty'],
                    'bom_loss_qty': line['bom_loss_qty'],
                    'bom_product_qty': line['bom_product_qty'],
                    'apply_product_qty': line['apply_product_qty'],
                    'body': line['body'],
                    'order_id':wizard_id.id,
                    'erp_id': line['erp_id'],
                })
            action = self.env.ref('fast_supplier_synergy.fast_create_material_requirements_wizard_action_apply_material').sudo().read()[0]
            action['res_id'] = wizard_id.id
            action['context'] = {'dialog_size': 'extra-modal-max-95'}
            return action
  


class FastBlankOrderMaterialRequirements(models.Model):
    _name = 'fast.blank.order.material.requirements'
    _description = '订单中心--物料需求'
    _order = 'outsource_order_blank_id'

 
    # 关联主表
    outsource_order_blank_id = fields.Many2one('fast.supplier.order.blank', string='所属空白版委外加工单',
                                               ondelete='cascade')
    cutting_order_blank_id = fields.Many2one('fast.supplier.order.blank', string='所属裁床订单', ondelete='cascade')

    product_id = fields.Integer(string='erp主辅料id', help="用于区分我这边的主辅料记录")
    conf_type = fields.Char(string='产品类型')

    product_default_code = fields.Char(string='编码')
    product_default_name = fields.Char(string='名称')
    color_value_name = fields.Char(string='颜色')
    color_cn_name = fields.Char(string='颜色')
    categ_name = fields.Char(string='分类')
    # 物料需求信息——数量
    product_qty = fields.Float(string='需求数', digits="Product Unit of Measure")
    # 物料流转信息
    apply_qty = fields.Float(string='已申请数', digits="Product Unit of Measure")
    ship_qty = fields.Float(string='实发数', digits="Product Unit of Measure")
    return_qty = fields.Float(string='退货数', digits="Product Unit of Measure")

    body = fields.Char(string='部位')
    product_spec_name = fields.Char(string='规格')
    product_spec_remark = fields.Text('规格备注')

    assist_uom_name = fields.Char(string='计量单位')
    uom_po_name = fields.Char(string='采购单位')



    # product_default_code = fields.Char(string='编码')
    # product_default_name = fields.Char(string='名称')
    # product_color_name = fields.Char(string='颜色')
    # f_width = fields.Char(string='边至边幅宽(cm)')
    # g_weight = fields.Char(string='克重')
    #
    # # 物料需求信息--价格信息
    # shipping_price = fields.Char(string='BOM米价')
    # shipping_price_total = fields.Char(string='BOM米价金额')
    # material_price = fields.Char(string='BOM公斤价')
    # material_price_total = fields.Char(string='BOM公斤价金额')
    # # currency_id = fields.Many2one('res.currency', '货币符号', default=lambda self: self.env.company.currency_id.id)
    #
    # assist_product_qty = fields.Char(string='BOM用量')
    # product_qty = fields.Char('需求数')
    #
    # # 物料流转信息
    # apply_qty = fields.Char(string='已申请数')
    # ship_qty = fields.Char(string='实发数')
    # return_qty = fields.Char(string='退货数')
    #
    # categ_name = fields.Char(string='分类')
    # product_spec_name = fields.Char(string='规格')
    # product_spec_remark = fields.Text('规格备注')
    #
    # assist_uom_name = fields.Char(string='计量单位')
    # uom_po_name = fields.Char(string='采购单位')


class ProcessCost(models.Model):
    _name = 'fast.process_cost'
    _description = '款式加工价格'
    _rec_name = 'name'


    blank_order_id = fields.Many2one('fast.supplier.order.blank', string='所属订单', ondelete='cascade')

    name = fields.Char(string='款式', help='空白版款号')
    partner_name = fields.Char(string='供应商', related='blank_order_id.processing_plant')
    process_price = fields.Float(string='工价', digits='Product Price')
    management_price = fields.Float(string='管理费', digits='Product Price')
    other_price = fields.Float(string='其他费用', digits='Product Price')
    price = fields.Float('加工费合计', compute='_compute_price', store=True, digits=(16, 4))
    bom_price = fields.Float(string='BOM成本', digits='Product Price')
    total_price = fields.Float(string='单件价格', compute='_compute_total_price', store=True, digits=(16, 4))
    remark = fields.Text('价格备注')


    @api.depends('process_price','management_price', 'other_price')
    def _compute_price(self):
        for res in self:
            res.price = res.process_price + res.management_price + res.other_price

    @api.depends('process_price', 'management_price', 'other_price', 'bom_price')
    def _compute_total_price(self):
        for res in self:
            res.price = res.process_price + res.management_price + res.other_price + res.bom_price


