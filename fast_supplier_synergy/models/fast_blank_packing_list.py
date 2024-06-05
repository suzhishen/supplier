# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools import groupby
import requests
import re
from odoo.exceptions import UserError, ValidationError
import traceback
import logging
import json

_logger = logging.getLogger(__name__)

Dev_url = 'http://192.168.6.50:10010'
BlankSize = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t', '4', '5', '6',
             '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']


class FastBlankPackingList(models.Model):
    _name = 'fast.blank.packing_list'
    _description = "装箱单"
    _rec_name = 'partner_name'

    # po = fields.Char(string='PO#')
    partner_name = fields.Char(string='加工厂')
    # tracking_number = fields.Char(string='装箱单号')
    tracking_number = fields.Char(string='装箱单号', default='New')
    shipping = fields.Char(string='运输方式')
    delivery_date = fields.Date(string='预计到货日期')
    total_quantity = fields.Integer(string='总装箱数量(件)', compute='_compute_total_quantity', store=True)
    total_received_quantity = fields.Integer(string='总收货数量(件)', compute='_compute_total_total_received_quantity',
                                             store=True)
    total_boxes = fields.Integer(string='总箱数', compute='_compute_total_boxes', store=True)
    synch_state = fields.Selection([('not_synch', '未同步'), ('have_synch', '已同步')], string='同步状态',
                                   default='not_synch')
    packing_list_detail_line = fields.One2many('fast.blank.packing_list_detail', 'packing_list_id',
                                               string='相关装箱单明细')

    # erp_blank_id = fields.Integer(string='ERP空白版ID', help='ERP系统中空白版ID')

    @api.model_create_multi
    def create(self, vals_list):
        for v in vals_list:
            if self.tracking_number == _('New') or not self.tracking_number:
                v['tracking_number'] = self.env['ir.sequence'].next_by_code('fast.blank.packing_list.seq') or 'New'
        return super(FastBlankPackingList, self).create(vals_list)

    def unlink(self):
        for record in self:
            record.mapped('packing_list_detail_line').mapped('packing_detail_follow_id').unlink()
        return super(FastBlankPackingList, self).unlink()

    @api.depends('packing_list_detail_line.quantity')
    def _compute_total_quantity(self):
        self.total_quantity = sum(self.packing_list_detail_line.mapped('quantity'))

    @api.depends('packing_list_detail_line')
    def _compute_total_boxes(self):
        self.total_boxes = len(set(self.packing_list_detail_line.mapped('box_number')))

    @api.depends('packing_list_detail_line.received_quantity')
    def _compute_total_total_received_quantity(self):
        self.total_received_quantity = sum(self.packing_list_detail_line.mapped('received_quantity'))

    @api.model
    def btn_synch_packing_list(self, args=[], **kwargs):
        """
        同步装箱信息到 ERP 系统
        :return:
        """
        records = self.search([('id', 'in', args)])
        # for item in list(set(records.mapped('delivery_date'))):
        for res in records:
            if not res.delivery_date or not res.shipping:
                raise UserError(f'请确认运输方式及预计到货日期已经填写！')
            if res.synch_state == 'have_synch':
                raise UserError(f'{res.po}该装箱单已经同步过了，请不要重复同步！')
        values = {
            'params': {
                'datas': []
            }
        }
        for index, item in enumerate(records):
            values['params']['datas'].append({
                # 'po': item.po,
                'partner_name': item.partner_name,
                'tracking_number': item.tracking_number,
                'delivery_date': item.delivery_date.strftime('%Y-%m-%d') if item.delivery_date else '',
            })
            detail_value = []
            for record in item.packing_list_detail_line:
                detail_value.append({
                    'po': record.po,
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
    def create_packing_detail_follow(self, args, **kwargs):
        """
        创建装箱操作明细跟进
        :return:
        """
        try:
            datas = kwargs.get('datas', False)
            po_name = datas.get('po', '不存在po')
            partner_name = datas.get('partner_name', '不存在po')
            product_color_code = datas.get('product_tmpl_code', '不存在product_tmpl_code')
            quantitys_list = kwargs.get('quantitys_list', [])
            updateData = kwargs.get('updateData', [])
            deleteData = kwargs.get('deleteData', '')
            hz_box_createDate_list = kwargs.get('hz_box_createDate_list', []) or []
            hz_box_updateData_list = kwargs.get('hz_box_updateData_list', []) or []

            packing_list_record = self.env['fast.blank.packing_list'].search(
                [('synch_state', '=', 'not_synch'), ('partner_name', '=', partner_name)])
            if not packing_list_record:
                packing_list_record = packing_list_record.create({'partner_name': datas.get('partner_name')})

            # 更新装箱操作跟进明细
            for k, v in updateData.items():
                order_detail = self.env['fast.packing_detail_follow'].sudo().browse(int(k))
                if order_detail.packing_quantity == int(v[0][0]) and order_detail.number_units == int(v[0][1]):
                    continue
                for v_item in v:
                    order_detail.packing_quantity = int(v_item[0])
                    order_detail.number_units = int(v_item[1])
                    order_detail.packing_list_detail_line.unlink()
                    value = []
                    # 创建装箱单
                    self.create_packing_list(order_detail, value)
                    packing_list_record.packing_list_detail_line = value

            # 删除装箱操作跟进明细, 包括混装数据
            if deleteData:
                deleteData = deleteData.split(',')
                deleteData = [int(i) for i in deleteData]
                order_detail = self.env['fast.packing_detail_follow'].sudo().search([('id', 'in', deleteData)])
                order_detail.packing_list_detail_line.unlink()
                order_detail.unlink()

            values = []
            # 添加装箱操作跟进明细
            for k, v in quantitys_list.items():
                product_name = product_color_code + '-' + k
                order_detail_id = self.env['fast.blank_order_detail'].search(
                    [('po_name', '=', po_name), ('product_name', '=', product_name)])
                if not order_detail_id:
                    raise ValidationError(f'未找到 {product_color_code} 请联系管理员！')
                for v_item in v:
                    res = self.env['fast.packing_detail_follow'].create({
                        'blank_order_detail_id': order_detail_id.id,
                        'product_color_name': order_detail_id.product_color_name,
                        'product_name': product_name,
                        'size': k,
                        'packing_quantity': v_item[0],
                        'number_units': v_item[1],
                    })
                    # 创建装箱单
                    self.create_packing_list(res, values)

                print(order_detail_id)

            # 创建混装数据
            packing_detail_follow_record = self.env['fast.packing_detail_follow'].search(
                [('mixed_stowage_sequence', '>', 0)])
            mixed_stowage_sequence = packing_detail_follow_record.mapped('mixed_stowage_sequence')
            if not packing_detail_follow_record:
                mixed_stowage_sequence = [0]
            sequence = max(mixed_stowage_sequence) + 1
            for index, box in enumerate(hz_box_createDate_list):
                sequence += index
                for k, v in box.items():
                    product_name = product_color_code + '-' + k
                    order_detail_id = self.env['fast.blank_order_detail'].search(
                        [('po_name', '=', po_name), ('product_name', '=', product_name)])
                    if not order_detail_id:
                        raise ValidationError(f'未找到 {product_color_code} 请联系管理员！')

                    blank_order_detail = self.env['fast.blank_order_detail'].sudo().search(
                        [('product_name', '=', product_name)], limit=1)
                    if not blank_order_detail:
                        continue

                    if not v or not v.replace(' ', ''):
                        continue

                    res = self.env['fast.packing_detail_follow'].create({
                        'blank_order_detail_id': order_detail_id.id,
                        'product_color_name': order_detail_id.product_color_name,
                        'product_name': product_name,
                        'size': k,
                        'packing_quantity': 1,
                        'number_units': int(v),
                        'mixed_stowage_sequence': sequence,
                    })
                    # 创建装箱单
                    self.create_packing_list(res, values)

            packing_list_record.packing_list_detail_line = values
            # number_data = []
            # for i in value:
            #     self.env['leda.box.number.difference'].search([('box_number','=',i['box_num'])])
            if not packing_list_record.packing_list_detail_line:
                packing_list_record.unlink()

            packing_detail_follow_record = self.env['fast.packing_detail_follow'].search(
                [('mixed_stowage_sequence', '>', 0)])
            mixed_stowage_sequence = packing_detail_follow_record.mapped('mixed_stowage_sequence')
            if not packing_detail_follow_record:
                mixed_stowage_sequence = [0]
            sequence = max(mixed_stowage_sequence) + 1

            # 更新混装数据
            records_ids = []
            for item in hz_box_updateData_list:
                for k, v in item.items():
                    record = self.env['fast.blank.packing_list_detail'].sudo().browse(int(k))
                    if not v:
                        v = 0
                    if record.quantity != int(v):
                        record.quantity = v
                        record.packing_detail_follow_id.number_units = int(v)
                        records_ids.append(record.id)
                    if not record.quantity:
                        record.packing_detail_follow_id.unlink()
                        record.unlink()

            return {
                'code': 200,
                'msg': '创建成功',
            }
        except Exception as e:
            _logger.error(traceback.format_exc())
            return False

    def create_packing_list(self, res, values):
        for item in range(res.packing_quantity):
            values.append((0, 0, {
                'po': res.po,
                'style_number': res.product_color_name.split('-')[0],
                'color': res.product_color_name.split('-')[-1],
                'product_color_name': res.product_color_name,
                'product_name': res.product_name,
                'size': res.size,
                'quantity': res.number_units,
                'mixed_stowage_sequence': res.mixed_stowage_sequence,
                'blank_order_detail_id': res.blank_order_detail_id.id,
                'packing_detail_follow_id': res.id,
            }))

    # @api.model
    # def create_blanK_packing_list(self, args, **kwargs):
    #     """
    #     创建空白版装箱单 (已废弃)
    #     :return:
    #     """
    #
    #     def add_detail(detail_value, quantity, blank_order_detail, mixed_stowage=False, mixed_stowage_sequence=False):
    #         """
    #         :param detail_value: 存储明细的列表
    #         :param quantity: 数量
    #         :param blank_order_detail: 订单明细记录
    #         :param mixed_stowage: 是否混装
    #         :return:
    #         """
    #         value = {
    #             'style_number': blank_order_detail.name,
    #             'color': blank_order_detail.product_color_name.split('-')[-1],
    #             'product_color_name': blank_order_detail.product_color_name,
    #             'product_name': blank_order_detail.product_name,
    #             'size': blank_order_detail.product_name.split('-')[-1],
    #             'quantity': quantity,
    #             'blank_order_detail_id': blank_order_detail.id,
    #         }
    #         if mixed_stowage_sequence:
    #             value.update({'mixed_stowage_sequence': mixed_stowage_sequence})
    #         detail_value.append((0, 0, value))
    #
    #     try:
    #         datas = kwargs.get('datas', False)
    #         po_name = datas.get('po', '不存在po')
    #         partner_name = datas.get('partner_name', '不存在po')
    #         quantitys_list = kwargs.get('quantitys_list', False)
    #         updateData_list = kwargs.get('updateData_list', False)
    #         hz_box_createDate_list = kwargs.get('hz_box_createDate_list', []) or []
    #         hz_box_updateData_list = kwargs.get('hz_box_updateData_list', []) or []
    #
    #         records_ids = []
    #         detail_records = []
    #         # 更新数量
    #         for k, v in updateData_list.items():
    #             record = self.env['fast.blank.packing_list_detail'].sudo().browse(int(k))
    #             if not v:
    #                 v = 0
    #             if record.quantity != int(v):
    #                 record.quantity = v
    #                 records_ids.append(record.id)
    #             if not record.quantity:
    #                 record.unlink()
    #
    #         detail_value = []
    #         quantity_list = []
    #         for k, v in quantitys_list.items():
    #             product_name = datas.get('product_tmpl_code', '') + '-' + k
    #             blank_order_detail = self.env['fast.blank_order_detail'].sudo().search(
    #                 [('product_name', '=', product_name)], limit=1)
    #             if not blank_order_detail:
    #                 continue
    #
    #             for item in v:
    #                 if not item or not item.replace(' ', ''):
    #                     continue
    #                 quantity_list.append({
    #                     'product_name': blank_order_detail.product_name,
    #                     'quantity': item,
    #                 })
    #                 add_detail(detail_value, item, blank_order_detail)
    #
    #         blank_packing_list = self.env['fast.blank.packing_list'].search(
    #             [('po', '=', po_name), ('synch_state', '=', 'not_synch')])
    #         mixed_stowage_sequence = list(
    #             set(blank_packing_list.packing_list_detail_line.mapped('mixed_stowage_sequence')))
    #         if not mixed_stowage_sequence:
    #             mixed_stowage_sequence = [0]
    #         sequence = max(mixed_stowage_sequence) + 1
    #
    #         # 更新混装数据
    #         for item in hz_box_updateData_list:
    #             for k, v in item.items():
    #                 record = self.env['fast.blank.packing_list_detail'].sudo().browse(int(k))
    #                 if not v:
    #                     v = 0
    #                 if record.quantity != int(v):
    #                     record.quantity = v
    #                     records_ids.append(record.id)
    #                 if not record.quantity:
    #                     record.unlink()
    #         # 创建混装数据
    #         for index, box in enumerate(hz_box_createDate_list):
    #             sequence += index
    #             for k, v in box.items():
    #                 product_name = datas.get('product_tmpl_code', '') + '-' + k
    #                 blank_order_detail = self.env['fast.blank_order_detail'].sudo().search(
    #                     [('product_name', '=', product_name)], limit=1)
    #                 if not blank_order_detail:
    #                     continue
    #
    #                 if not v or not v.replace(' ', ''):
    #                     continue
    #                 quantity_list.append({
    #                     'product_name': blank_order_detail.product_name,
    #                     'quantity': v,
    #                 })
    #                 add_detail(detail_value, v, blank_order_detail, True, sequence)
    #
    #         if blank_packing_list:
    #             now_packing_list_detail_ids = blank_packing_list.packing_list_detail_line.ids
    #             blank_packing_list.write({
    #                 'packing_list_detail_line': detail_value,
    #             })
    #             update_packing_list_detail_ids = blank_packing_list.packing_list_detail_line.ids
    #             detail_records.extend(list(set(update_packing_list_detail_ids) - set(now_packing_list_detail_ids)))
    #         else:
    #             blank_packing_list = self.env['fast.blank.packing_list'].search([('po', '=', po_name)])
    #             tracking_number = blank_packing_list.mapped('tracking_number')
    #             if tracking_number:
    #                 max_number = max([re.search(r'[A-Z](\d+-\d+-(\d+))', s).group(2) for s in tracking_number])
    #                 next_number = int(max_number) + 1
    #                 if next_number < 10:
    #                     tracking_number = po_name + '-0' + str(next_number)
    #             else:
    #                 tracking_number = po_name + '-01'
    #
    #             values = {
    #                 'po': po_name,
    #                 'partner_name': partner_name,
    #                 'tracking_number': tracking_number,
    #                 'packing_list_detail_line': detail_value,
    #             }
    #             records = blank_packing_list.create(values)
    #             records_ids += records.packing_list_detail_line.ids
    #         return {
    #             'code': 200,
    #             'msg': '创建成功',
    #             'data': quantity_list,
    #             'records_ids': records_ids + detail_records,
    #         }
    #     except Exception as e:
    #         _logger.error(traceback.format_exc())
    #         return False

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

            # 过滤相同的箱号
            box_number_list = []
            record_list = []
            for record in order.packing_list_detail_line:
                if record.box_number not in box_number_list:
                    box_number_list.append(record.box_number)
                    record_list.append(record)

            for box_number, rows in groupby(record_list, key=lambda x: x.box_number):
                html = """   """
                y = 611
                for line in rows:
                    html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y,
                                                                                                  product_name=line.product_name + ' / ' + str(
                                                                                                      line.quantity))
                    y += 72
                    html += '\n'
                    html += """^FT510,1000^A0N,67,63^FH\^CI28^FD{sequence}^FS^CI27   """.format(sequence=line.sequence)
                    html += '\n'
                    print_data += upc_tp.content.format(box_number=box_number,
                                                        partner_name=order.partner_name or '',
                                                        po=line.po,
                                                        date=order.delivery_date and order.delivery_date.strftime(
                                                            '%Y/%m/%d') or line.create_date.strftime('%Y/%m/%d'),
                                                        html=html
                                                        )

            return print_data


class FastBlankPackingListDetail(models.Model):
    _name = 'fast.blank.packing_list_detail'
    _description = "装箱单明细"

    erp_id = fields.Integer('erp_id')
    packing_list_id = fields.Many2one('fast.blank.packing_list', string='所属装箱单', ondelete='cascade')
    blank_order_detail_id = fields.Many2one('fast.blank_order_detail', string='所属订单明细', ondelete='cascade')
    packing_detail_follow_id = fields.Many2one('fast.packing_detail_follow', string='所属装箱明细跟进',
                                               ondelete='cascade')
    # po = fields.Char(string='PO#', related='packing_list_id.po', store=True)
    po = fields.Char(string='PO#')
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
    mixed_stowage_sequence = fields.Integer('混装序号')

    @api.depends('quantity', 'packing_list_id', 'blank_order_detail_id')
    def _compute_sequence(self):
        ids = []
        for detail in self:
            if detail.id in ids:
                continue
            detail_list = self.search([('id', 'in', detail.packing_list_id.packing_list_detail_line.ids)],
                                      order='id asc')
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

    @api.depends('quantity', 'received_quantity')
    def _compute_difference_quantity(self):
        for record in self:
            record.difference_quantity = record.quantity - record.received_quantity

    @api.model_create_multi
    def create(self, vals_list):
        box_number = ''
        mixed_stowage_sequence = False
        for v in vals_list:
            if v.get('mixed_stowage_sequence') == None or not v.get('mixed_stowage_sequence'):
                v['box_number'] = self.env['ir.sequence'].next_by_code('fast.blank.packing_list_detail.seq') or 'New'
            elif mixed_stowage_sequence != v.get('mixed_stowage_sequence'):
                v['box_number'] = self.env['ir.sequence'].next_by_code('fast.blank.packing_list_detail.seq') or 'New'
                box_number = v['box_number']
                mixed_stowage_sequence = v.get('mixed_stowage_sequence')
            else:
                v['box_number'] = box_number
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
            html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y,
                                                                                          product_name=order.product_name + ' / ' + str(
                                                                                              order.quantity))
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
            html += """^FT11,{y}^A0N,55,55^FH\^CI28^FD{product_name}^FS^CI27   """.format(y=y,
                                                                                          product_name=order.product_name + ' / ' + str(
                                                                                              order.quantity))
            y += 72
            html += '\n'
            html += """^FT510,1000^A0N,67,63^FH\^CI28^FD{sequence}^FS^CI27   """.format(sequence=order.sequence)
            html += '\n'
            print_data += upc_tp.content.format(box_number=order.box_number,
                                                partner_name=order.processing_plant or '',
                                                po=order.po,
                                                date=order.packing_list_id.delivery_date and order.packing_list_id.delivery_date.strftime(
                                                    '%Y/%m/%d') or order.create_date.strftime('%Y/%m/%d'),
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
        po = kwargs.get('po') or ''
        product_code = kwargs.get('product_code') or ''
        group_records = self.search([]).read_group(
            domain=[('product_color_name', '=', product_code)],
            fields=list(self._fields.keys()),
            groupby='product_name'
        )
        data = []
        for record in group_records:
            data.append({
                'size': record['product_name'].split('-')[-1],
                'quantity': record['quantity'],
            })
        data = sorted(data, key=lambda x: BlankSize.index(x['size'].lower()))
        records_detail = self.search(
            [('product_color_name', '=', kwargs.get('product_code')), ('mixed_stowage_sequence', '=', False)],
            order='id asc')
        # 混装数据展示返回 html 页面
        mixed_stowage_records_detail = self.search(
            [('product_color_name', '=', kwargs.get('product_code')), ('mixed_stowage_sequence', '>', 0),
             ('synch_state', '=', 'not_synch')], order='id asc')
        mixed_stowage_records_json = mixed_stowage_records_detail.jsonify(
            ['id', 'size', 'quantity', 'synch_state', 'mixed_stowage_sequence', ('packing_detail_follow_id', ['id'])])
        mixed_stowage_sequence_value = {}
        for item in mixed_stowage_records_json:
            mixed_stowage_sequence_value.update({item['mixed_stowage_sequence']: []})
        for item in mixed_stowage_records_json:
            mixed_stowage_sequence_value[item['mixed_stowage_sequence']].append(item)
        existing_data = records_detail.jsonify(['id', 'size', 'quantity', 'synch_state'])
        # 装箱操作返回非混装数据到 html 页面
        domain = [('po', '=', po), ('product_color_name', '=', product_code), ('mixed_stowage_sequence', '=', False),
                  ('synch', '=', False)]
        packing_detail_follow_res = self.env['fast.packing_detail_follow'].search(domain, order='id asc')
        packing_detail_follow_val = packing_detail_follow_res.jsonify(
            ['id', 'size', 'packing_quantity', 'number_units'])
        # 超出占比配置
        packing_follow_config = self.env['fast.packing_follow.config'].sudo().search([], order='id asc')
        packing_follow_config_val = packing_follow_config.jsonify(['id', 'number', 'percentage'])
        values = {
            'data': data,
            'existing_data': existing_data,
            'mixed_stowage_sequence_value': mixed_stowage_sequence_value,
            'packing_detail_follow_val': packing_detail_follow_val,
            'packing_follow_config_val': packing_follow_config_val,
        }
        return values

    @api.model
    def get_rep_size_list(self):
        """ 调用接口，获取 erp 码数 """
        response = requests.get(url=f'{Dev_url}/leda/fast_size_group', params={})
        print(response.json())
        return response.json()
        # return {"code":"2000","msg":"成功","data":{"t":["XXS","XS","S","M","L","XL","2XL","3XL","4XL","5XL","6XL"],"s":["2T","3T","4T","4","5","6","7","8","8/10","10/12","12/14","14/16","16","18/20"]}}

    def get_records_format_data(self):
        record = self.env['fast.blank.packing_list_detail'].sudo().search([('receive_state', '=', 'have_receive')],
                                                                          order='id asc')
        data = record.jsonify(
            ['id', 'box_number', 'po', 'style_number', 'color', 'size', 'quantity', 'received_quantity',
             'difference_quantity'])

        value = {}
        for item in data:
            value.update({item['box_number']: []})
        for item in data:
            value[item['box_number']].append(item)
        new_data = []
        str = ''
        for val in value.values():
            new_data_val = {}
            for index, item in enumerate(val):
                if index == 0:
                    new_data_val.update({
                        'box_number': item['box_number'],
                        'po': item['po'],
                        'style_number': item['style_number'],
                        'color': item['color'],
                        'size': [item['size']],
                        'quantity': [item['quantity']],
                        'received_quantity': [item['received_quantity']],
                        'difference_quantity': [item['difference_quantity']],
                    })
                    if item['difference_quantity'] != 0:
                        str += f'{item["size"]} {item["quantity"]}/{item["received_quantity"]}/{item["difference_quantity"]}'
                        if index + 1 != len(val):
                            str += ' --- '
                    else:
                        str += f'{item["size"]} {item["quantity"]}'
                else:
                    if item['difference_quantity'] != 0:
                        str += f'{item["size"]} {item["quantity"]}/{item["received_quantity"]}/{item["difference_quantity"]}'
                        if index + 1 != len(val):
                            str += ' --- '
                    else:
                        str += f'{item["size"]} {item["quantity"]}'
            new_data_val.update({'str': str})
            str = ''
            new_data.append(new_data_val)
        return json.dumps({
            "code": 200,
            "msg": "请求成功",
            'data': new_data
        })

        # data = []
        # for record in self:
        #     box_line = []
        #     for line in record.detail_line:
        #         box_line.append({
        #             'id': line,
        #             'product_id': line.product_id,
        #             'size_name': line.size_name,
        #             'product_qty': line.product_qty,
        #             'practical_qty': line.practical_qty,
        #         })
        #     blank_size = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t',
        #                   '4', '5', '6', '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']
        #     box_line = sorted(box_line, key=lambda k: blank_size.index(k['size_name'].lower()), reverse=False)
        #     data.append({
        #         'box_number': record.box_number,
        #         'total_packing_qty': record.total_packing_qty,
        #         'total_product_qty': record.total_product_qty,
        #         'total_diff_qty': record.total_diff_qty,
        #         'po': record.po,
        #         'product_tmpl_id': record.product_tmpl_id,
        #         'product_configuration_id': record.product_configuration_id,
        #         'box_line': box_line
        #     })
        # return data

    @api.model
    def packing_list_difference(self):
        record = self.env['fast.blank.packing_list_detail'].sudo().search([('receive_state', '=', 'have_receive')],
                                                                          order='id asc')
        data = record.jsonify(
            ['id', 'box_number', 'po', 'style_number', 'color', 'size', 'quantity', 'received_quantity',
             'difference_quantity'])
        value = {}
        for item in data:
            value.update({item['box_number']: []})
        for item in data:
            value[item['box_number']].append(item)
        new_data = []
        for val in value.values():
            new_data_val = {}
            for index, item in enumerate(val):
                if index == 0:
                    new_data_val.update({
                        'po': item['po'],  # 订单号
                        'style_number': item['style_number'],  # 款号
                        'color': item['color'],  # 颜色
                        'box_number': item['box_number'],  # 箱号
                        'hz_datas': [],  # 尺码 / 装箱件数 / 实收件数 / 差异件数
                        'index': 0,
                        'quantity_sum': 0,
                        'received_quantity_sum': 0,
                        'difference_quantity_sum': 0
                    })
                new_data_val['hz_datas'].append({
                    'size': item['size'],
                    'quantity': item['quantity'],
                    'received_quantity': item['received_quantity'],
                    'difference_quantity': item['difference_quantity'],
                })
                new_data_val['index'] = index + 1
                new_data_val['quantity_sum'] += int(item['quantity'])
                new_data_val['received_quantity_sum'] += int(item['received_quantity'])
                new_data_val['difference_quantity_sum'] += int(item['difference_quantity'])
            new_data.append(new_data_val)
        return json.dumps({
            "code": 200,
            "msg": "请求成功",
            'data': new_data
        })


class FastPackingDetailFollow(models.Model):
    _name = 'fast.packing_detail_follow'
    _description = "装箱操作明细跟进"

    packing_list_detail_line = fields.One2many('fast.blank.packing_list_detail', 'packing_detail_follow_id',
                                               string='相关装箱单明细')
    blank_order_detail_id = fields.Many2one('fast.blank_order_detail', string='所属订单明细', ondelete='cascade')
    po = fields.Char(string='PO#', related='blank_order_detail_id.po_name', store=True)
    processing_plant = fields.Char(related='blank_order_detail_id.processing_plant', string='加工厂', store=True)
    synch_state = fields.Selection([('not_create', '未生成'), ('have_create', '已生成')], string='生成状态',
                                   help="是否生成装箱单状态")
    product_color_name = fields.Char(string='款色')
    product_name = fields.Char(string='产品', help='变体')
    size = fields.Char(string='尺码')
    packing_quantity = fields.Integer(string='箱数')
    number_units = fields.Integer(string='每箱件数')
    mixed_stowage_sequence = fields.Integer('混装序号')
    synch = fields.Boolean(string='是否已同步', compute='_compute_synch', default=False, store=True)

    @api.depends('packing_list_detail_line', 'packing_list_detail_line.synch_state')
    def _compute_synch(self):
        for record in self:
            synch_state_list = record.mapped('packing_list_detail_line').mapped('synch_state')
            if 'have_synch' in synch_state_list:
                record.synch = True
            else:
                record.synch = False
