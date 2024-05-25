# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools import groupby
import requests
import re
from odoo.exceptions import UserError, ValidationError

BlankSize = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t', '4', '5', '6', '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']


class FastBlankPackingList(models.Model):
    _name = "fast.blank.packing_list"
    _description = "空白版装箱单"
    _rec_name = 'po'

    po = fields.Char(string='PO#')
    partner_name = fields.Char(string='加工厂')
    tracking_number = fields.Char(string='装箱单号')
    delivery_date = fields.Date(string='预计到货日期')
    total_quantity = fields.Integer(string='总装箱数量(件)', compute='_compute_total_quantity', store=True)
    total_received_quantity = fields.Integer(string='总收货数量(件)', compute='_compute_total_total_received_quantity', store=True)
    total_boxes = fields.Integer(string='总箱数', compute='_compute_total_boxes', store=True)
    synch_state = fields.Selection([('not_synch', '未同步'), ('have_synch', '已同步')], string='同步状态', default='not_synch')
    packing_list_detail_line = fields.One2many('fast.blank.packing_list_detail', 'packing_list_id', string='相关装箱单明细')

    # erp_blank_id = fields.Integer(string='ERP空白版ID', help='ERP系统中空白版ID')

    @api.depends('packing_list_detail_line.quantity')
    def _compute_total_quantity(self):
        self.total_quantity = sum(self.packing_list_detail_line.mapped('quantity'))

    @api.depends('packing_list_detail_line')
    def _compute_total_boxes(self):
        self.total_boxes = len(self.packing_list_detail_line)

    @api.depends('packing_list_detail_line.received_quantity')
    def _compute_total_total_received_quantity(self):
        self.total_received_quantity = sum(self.packing_list_detail_line.mapped('received_quantity'))


    @api.model
    def btn_synch_packing_list(self, args=[], **kwargs):
        """
        同步装箱信息到 ERP 系统
        :return:
        """
        Dev_url = 'http://192.168.6.50:10010'
        records = self.search([('id', 'in', args)])
        # for item in list(set(records.mapped('delivery_date'))):
        for res in records:
            if not res.delivery_date:
                raise UserError(f'请确认{res.po}预计到货日期已经填写！')
            if res.synch_state == 'have_synch':
                raise UserError(f'{res.po}该装箱单已经同步过了，请不要重复同步！')
        values = {
            'params': {
                'datas': []
            }
        }
        for index, item in enumerate(records):
            values['params']['datas'].append({
                'po': item.po,
                'partner_name': item.partner_name,
                'tracking_number': item.tracking_number,
                'delivery_date': item.delivery_date.strftime('%Y-%m-%d') if item.delivery_date else '',
            })
            detail_value = []
            for record in item.packing_list_detail_line:
                detail_value.append({
                    'box_number': record.box_number,
                    'product_name': record.product_name,
                    'quantity': record.quantity,
                    # 'style_number': record.style_number,
                    # 'color': record.color,
                    # 'product_color_name': record.product_color_name,
                })
            values['params']['datas'][index].update({'detail_datas': detail_value})

        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=f'{Dev_url}/leda/update_package', json=values, headers=headers)
        result = response.json().get('result', False)
        if not (result and result.get('code', False) and result.get('code', False) == 200):
            raise UserError(response.text)
        else:
            records.synch_state = 'have_synch'

    @api.model
    def create_blanK_packing_list(self, args, **kwargs):
        """
        创建空白版装箱单
        :return:
        """
        try:
            datas = kwargs.get('datas', False)
            po_name = datas.get('po', '不存在po')
            partner_name = datas.get('partner_name', '不存在po')
            quantitys_lsit = kwargs.get('quantitys_lsit', False)
            updateDate_lsit = kwargs.get('updateDate_lsit', False)
            hz_updateDate_lsit = kwargs.get('hz_updateDate_lsit', False)

            records_ids = []
            detail_records = []
            # 更新数量
            for k, v in updateDate_lsit.items():
                record = self.env['fast.blank.packing_list_detail'].sudo().browse(int(k))
                if record.quantity != int(v):
                    record.quantity = v
                    records_ids.append(record.id)
                if not record.quantity:
                    record.unlink()

            detail_value = []
            quantity_list = []
            for k, v in quantitys_lsit.items():
                product_name = datas.get('product_tmpl_code', '') + '-' + k
                blank_order_detail = self.env['fast.blank_order_detail'].sudo().search(
                    [('product_name', '=', product_name)], limit=1)
                if not blank_order_detail:
                    continue

                for item in v:
                    if not v or not item.replace(' ', ''):
                        continue
                    quantity_list.append({
                        'product_name': blank_order_detail.product_name,
                        'quantity': item,
                    })

                    detail_value.append((0, 0, {
                        'style_number': blank_order_detail.name,
                        'color': blank_order_detail.product_color_name.split('-')[-1],
                        'product_color_name': blank_order_detail.product_color_name,
                        'product_name': blank_order_detail.product_name,
                        'size': blank_order_detail.product_name.split('-')[-1],
                        'quantity': item,
                        'blank_order_detail_id': blank_order_detail.id,
                    }))

            blank_packing_list = self.env['fast.blank.packing_list'].search(
                [('po', '=', po_name), ('synch_state', '=', 'not_synch')])
            if blank_packing_list:
                now_packing_list_detail_ids = blank_packing_list.packing_list_detail_line.ids
                blank_packing_list.write({
                    'packing_list_detail_line': detail_value,
                })
                update_packing_list_detail_ids = blank_packing_list.packing_list_detail_line.ids
                detail_records.extend(list(set(update_packing_list_detail_ids) - set(now_packing_list_detail_ids)))
            else:
                blank_packing_list = self.env['fast.blank.packing_list'].search([('po', '=', po_name)])
                tracking_number = blank_packing_list.mapped('tracking_number')
                if tracking_number:
                    max_number = max([re.search(r'[A-Z](\d+-\d+-(\d+))', s).group(2) for s in tracking_number])
                    next_number = int(max_number) + 1
                    if next_number < 10:
                        tracking_number = po_name + '-0' + str(next_number)
                else:
                    tracking_number = po_name + '-01'

                values = {
                    'po': po_name,
                    'partner_name': partner_name,
                    'tracking_number': tracking_number,
                    'packing_list_detail_line': detail_value,
                }
                records = blank_packing_list.create(values)
                records_ids += records.packing_list_detail_line.ids
            return {
                'code': 200,
                'msg': '创建成功',
                'data': quantity_list,
                'records_ids': records_ids + detail_records,
            }
        except Exception as e:
            return False

    def btn_print_packing_list_action(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'PrintProductBlankClp',
            'name': '打印箱二维码',
            'target': 'new'
        }

    def get_clp_label_zpl_data(self):
        """
        打印箱二维码（多条）
        :return:
        """
        print_data = ''
        for order in self:
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'Product_Blank_CLP_LABEL')], limit=1)
            print_data += upc_tp.header_content
            for box_number, rows in groupby(order.packing_list_detail_line, key=lambda x: x.box_number):
                html = """   """
                y = 611
                for line in rows:
                    html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y, product_name=line.product_name + ' / ' + str(line.quantity))
                    y += 72
                    html += '\n'
                    html += """^FT510,1000^A0N,67,63^FH\^CI28^FD{sequence}^FS^CI27   """.format(sequence=line.sequence)
                    html += '\n'
                    print_data += upc_tp.content.format(box_number=box_number,
                                                        partner_name=order.partner_name or '',
                                                        po=order.po,
                                                        date=order.delivery_date and order.delivery_date.strftime(
                                                            '%Y/%m/%d') or line.create_date.strftime('%Y/%m/%d'),
                                                        html=html
                                                        )

            return print_data


class FastBlankPackingListDetail(models.Model):
    _name = 'fast.blank.packing_list_detail'
    _description = "空白版装箱单明细"

    erp_id = fields.Integer('erp_id')
    packing_list_id = fields.Many2one('fast.blank.packing_list', string='所属装箱单', ondelete='cascade')
    blank_order_detail_id = fields.Many2one('fast.blank_order_detail', string='所属订单明细', ondelete='cascade')
    po = fields.Char(string='PO#', related='packing_list_id.po', store=True)
    box_number = fields.Char(string='C/T NO箱号', default='New')
    processing_plant = fields.Char(related='packing_list_id.partner_name', string='加工厂', store=True)
    synch_state = fields.Selection(related="packing_list_id.synch_state", string='同步状态', store=True)
    style_number = fields.Char(string='STYLE# 款号')
    color = fields.Char(string='颜色')
    product_color_name = fields.Char(string='款色')
    product_name = fields.Char(string='产品', help='变体')
    size = fields.Char(string='尺码')
    quantity = fields.Integer(string='数量', default=0)
    received_quantity = fields.Integer(string='已收货数量', default=0)
    difference_quantity = fields.Integer(string='差异数量', compute='_compute_difference_quantity', store=True)
    receive_state = fields.Selection([('not_receive', '未收货'), ('have_receive', '已收货')], string='收货状态',
                                     default='not_receive', compute='_compute_receive_state', store=True)
    sequence = fields.Integer(string='序号', compute='_compute_sequence', store=True)

    @api.depends('quantity', 'packing_list_id', 'blank_order_detail_id')
    def _compute_sequence(self):
        ids = []
        for detail in self:
            if detail.id in ids:
                continue
            detail_list = self.search([('id', 'in', detail.packing_list_id.packing_list_detail_line.ids)], order='id asc')
            for index, item in enumerate(detail_list):
                item.sequence = index + 1
                ids.append(item.id)

    @api.depends('quantity', 'received_quantity')
    def _compute_receive_state(self):
        for record in self:
            if record.received_quantity:
                record.receive_state = 'have_receive'
            else:
                record.receive_state = 'not_receive'

    @api.depends('quantity','received_quantity')
    def _compute_difference_quantity(self):
        for record in self:
            record.difference_quantity = record.quantity - record.received_quantity

    @api.model_create_multi
    def create(self, vals_list):
        for v in vals_list:
            v['box_number'] = self.env['ir.sequence'].next_by_code('fast.blank.packing_list_detail.seq') or 'New'
        return super(FastBlankPackingListDetail, self).create(vals_list)

    def btn_one_print_packing_list_action(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'PrintOneProductBlankClp',
            'name': '打印箱二维码',
            'target': 'new',
        }

    def get_save_clp_label_zpl_data(self, **kwargs):
        """
        打印箱二维码（保存后立刻打印）
        :return:
        """
        print_data = ''
        records_ids = kwargs.get('records_ids', False)
        print('records_ids', records_ids)
        records = self.search([('id', 'in', records_ids)], order='id asc')
        for order in records:
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'Product_Blank_CLP_LABEL')], limit=1)
            print_data += upc_tp.header_content
            html = """   """
            y = 611
            html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y, product_name=order.product_name + ' / ' + str(order.quantity))
            y += 72
            html += '\n'
            html += """^FT510,1000^A0N,67,63^FH\^CI28^FD{sequence}^FS^CI27   """.format(sequence=order.sequence)
            html += '\n'
            print_data += upc_tp.content.format(box_number=order.box_number,
                                                partner_name=order.processing_plant or '',
                                                po=order.packing_list_id.po,
                                                date=order.packing_list_id.delivery_date and order.packing_list_id.delivery_date.strftime(
                                                    '%Y/%m/%d') or order.create_date.strftime('%Y/%m/%d'),
                                                html=html
                                                )
        return print_data

    def get_one_clp_label_zpl_data(self):
        """
        打印箱二维码（单条）
        :return:
        """
        print_data = ''
        for order in self:
            upc_tp = self.env['zebra.upc.template'].search([('code', '=', 'Product_Blank_CLP_LABEL')], limit=1)
            print_data += upc_tp.header_content
            html = """   """
            y = 611
            html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y, product_name=order.product_name + ' / ' + str(order.quantity))
            y += 72
            html += '\n'
            html += """^FT510,1000^A0N,67,63^FH\^CI28^FD{sequence}^FS^CI27   """.format(sequence=order.sequence)
            html += '\n'
            print_data += upc_tp.content.format(box_number=order.box_number,
                                                partner_name=order.processing_plant or '',
                                                po=order.packing_list_id.po,
                                                date=order.packing_list_id.delivery_date and order.packing_list_id.delivery_date.strftime('%Y/%m/%d') or order.create_date.strftime('%Y/%m/%d'),
                                                html=html
                                                )
            return print_data

    @api.model
    def get_packed_list_datas(self, **kwargs):
        """
        订单跟进 - 欠数明细 以及 已装箱明细 数据的更新
        :param kwargs: dict   款色, { product_code: 'M30050-GRY' }
        :return: [{}]
        """
        records = self.search([]).read_group(
            domain=[('product_color_name', '=', kwargs.get('product_code'))],
            fields=list(self._fields.keys()),
            groupby='product_name'
        )
        values = []
        for record in records:
            values.append({
                'size': record['product_name'].split('-')[-1],
                'quantity': record['quantity'],
            })
        values = sorted(values, key=lambda x: BlankSize.index(x['size'].lower()))
        records_detail = self.search([('product_color_name', '=', kwargs.get('product_code'))], order='id asc')
        existing_data = records_detail.jsonify(['id', 'size', 'quantity', 'synch_state'])
        if not records_detail:
            raise UserError(f'未找到该记录')
        date_expected = records_detail[0].blank_order_detail_id.date_expected
        return values, existing_data, date_expected
