from odoo.http import content_disposition, dispatch_rpc, request, SessionExpiredException
from odoo.addons.fast_supplier_synergy.controllers.exception import OdooCustomHTTPException
from odoo import http
import datetime
import requests
import logging
import json
import odoo
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import time
import base64
import re
import traceback
from odoo.exceptions import UserError, ValidationError
from pypinyin import pinyin, Style
from passlib.context import CryptContext
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

Opener = False

db_monodb = False
all_dbs = http.db_list(force=True)
if len(all_dbs) == 1:
    db_monodb = all_dbs[0]

BlankSize = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t', '4', '5', '6',
             '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']


class ErpController(http.Controller):
    def add_one2many_datas(self, datas_list):
        datas = []
        for item in datas_list:
            datas.append((0, 0, item))
        return datas

    """同步供应商FOB价格"""
    @http.route('/erp/unlink_supplier_quotation', type='json', auth="none", csrf=False, methods=['POST'])
    def unlink_supplier_quotation(self,**kwargs):
        try:
            json_data = kwargs.get('data')
            for item in json_data:
                supplier_quotation = None
                if item['type'] == 'FOB':
                    supplier_quotation = request.env['fast.overall.outsourcing.supplier.quotation'].sudo().search([('erp_id','=',item.get('erp_id',''))])
                elif item['type'] == 'MTP':
                    supplier_quotation = request.env['fast.production.processes.supplier.quotation'].sudo().search([('erp_id','=',item.get('erp_id',''))])
                if supplier_quotation:
                    supplier_quotation.sudo().unlink()
            return {'code': 200, 'msg': '同步成功'}
        except Exception as e:
               return {'code': 400, 'msg': '同步失败'}


    @http.route('/erp/onchange_outsourcing_supplier_quotation', type='json', auth="none", csrf=False, methods=['POST'])
    def onchange_outsourcing_supplier_quotation(self, **kwargs):
       try:
           json_data = kwargs.get('data')
           for item in json_data:
               product_configuration_id = request.env['fast.blank.configuration'].sudo().search([('default_code', '=', item.get('product_configuration_id'))])
               if product_configuration_id:
                   item.pop('product_configuration_id')
                   # 如果存在先删除再创建
                   supplier_quotation = request.env['fast.overall.outsourcing.supplier.quotation'].sudo().search([('erp_id','=',item.get('erp_id',''))])
                   supplier_quotation and supplier_quotation.sudo().unlink()
                   def find_create_company_user(item):
                       partner_id = item.get('partner_id', False) or ''
                       if not partner_id:
                           _logger.error("blank_basics_synchronous 未找到供应商参数")
                           return {
                               'code': 400,
                               'msg': '未找到供应商参数'
                           }
                       company_record = request.env['res.company'].search([('code', '=', item['partner_id']['code'])])
                       new_company = company_record
                       if not company_record:
                           admin_user = request.env.ref('base.user_root')
                           new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                               'name': item['partner_id']['name'],
                               'erp_supplier_id': item['partner_id']['id'],
                               'code': item['partner_id']['code'],
                               'currency_id': 7,
                           })
                           pinyin_name = pinyin(item['partner_id']['name'], style=Style.NORMAL)
                           name = ''.join([syllable[0] for syllable in pinyin_name])
                           request.env['res.users'].with_user(admin_user).sudo().create({
                               'name': name,
                               'login': name,
                               'company_ids': [(6, 0, new_company.ids)],
                               'company_id': new_company.id,
                               'password': name,
                           })
                       return new_company.id
                   new_company = find_create_company_user(item)
                   item['company_id'] = new_company
                   product_configuration_id.blank_supplier_quotation_lines = [(0, 0, item)]
           return {
               'code': 200,
               'msg': '同步成功'
           }
       except Exception as e:
           _logger.error(traceback.format_exc())
           return {
               'code': 400,
               'msg': '同步失败'
           }

    """同步供应商MTP价格"""
    @http.route('/erp/onchange_production_supplier_quotation', type='json', auth="none", csrf=False, methods=['POST'])
    def onchange_production_supplier_quotation(self, **kwargs):
        try:
            json_data = kwargs.get('data')
            for item in json_data:
                product_configuration_id = request.env['fast.blank.configuration'].sudo().search(
                    [('default_code', '=', item.get('product_configuration_id'))])

                # 如果存在先删除再创建
                if product_configuration_id:
                    item.pop('product_configuration_id')
                    supplier_quotation = request.env['fast.production.processes.supplier.quotation'].sudo().search([('erp_id','=',item.get('erp_id',''))])
                    supplier_quotation and supplier_quotation.sudo().unlink()

                    def find_create_company_user(item):
                        partner_id = item.get('partner_id', False) or ''
                        if not partner_id:
                            _logger.error("blank_basics_synchronous 未找到供应商参数")
                            return {
                                'code': 400,
                                'msg': '未找到供应商参数'
                            }
                        company_record = request.env['res.company'].sudo().search([('code', '=', item['partner_id']['code'])])
                        new_company = company_record
                        if not company_record:
                            admin_user = request.env.ref('base.user_root')
                            new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                                'name': item['partner_id']['name'],
                                'erp_supplier_id': item['partner_id']['id'],
                                'code': item['partner_id']['code'],
                                'currency_id': 7,
                            })
                            pinyin_name = pinyin(item['partner_id']['name'], style=Style.NORMAL)
                            name = ''.join([syllable[0] for syllable in pinyin_name])
                            request.env['res.users'].with_user(admin_user).sudo().create({
                                'name': name,
                                'login': name,
                                'company_ids': [(6, 0, new_company.ids)],
                                'company_id': new_company.id,
                                'password': name,
                            })
                        return new_company.id

                    new_company = find_create_company_user(item)
                    item['company_id'] = new_company
                    product_configuration_id.blank_processes_supplier_quotation_lines = [(0, 0, item)]
            return {
                'code': 200,
                'msg': '同步成功'
            }

        except Exception as e:
            return {
                'code': 400,
                'msg': '同步失败'
            }
    @http.route('/erp/unlink_files', type='json', auth="none", csrf=False, methods=['POST'])
    def unlink_files(self, **kwargs):
        """ERP端删除文件，协同端也自动删除文件"""
        try:
            json_data = kwargs.get('data')
            attachment_id = request.env['ir.attachment'].sudo().search([('erp_id', '=', json_data.get('erp_id', ''))])
            process_categ_id = request.env.ref('fast_attachment.ir_attachment_category_process_sheet')
            diagram_categ_id = request.env.ref('fast_attachment.ir_attachment_category_frame_diagram')
            size_table_categ_id = request.env.ref('fast_attachment.ir_attachment_category_size_table')
            res_id = request.env['fast.blank.configuration'].sudo().browse(attachment_id.res_id)
            if attachment_id.categ_id == process_categ_id:
                res_id.process_attr_last_update_date = (datetime.datetime.now() + relativedelta(hours=8)).strftime('%Y/%m/%d  %H:%M')
            elif attachment_id.categ_id == diagram_categ_id:
                res_id.diagram_attr_last_update_date = (datetime.datetime.now() + relativedelta(hours=8)).strftime('%Y/%m/%d  %H:%M')
            elif attachment_id.categ_id == size_table_categ_id:
                res_id.size_attr_last_update_date = (datetime.datetime.now() + relativedelta(hours=8)).strftime('%Y/%m/%d  %H:%M')
            attachment_id.unlink()
        except Exception as e:
            return {
                'code':400,
                'msg':'删除失败'
            }
        return {
            'code':200,
            'msg':'删除成功'
        }

    @http.route('/erp/onchange_basics_info', type='json', auth="none", csrf=False, methods=['POST'])
    def onchange_basics_info(self, **kwargs):
        def find_create_company_user(item):
            partner_id = item.get('partner_id', False) or ''
            if not partner_id:
                _logger.error("blank_basics_synchronous 未找到供应商参数")
                return {
                    'code': 400,
                    'msg': '未找到供应商参数'
                }
            company_record = request.env['res.company'].search([('code', '=', item['partner_id']['code'])])
            new_company = company_record
            if not company_record:
                admin_user = request.env.ref('base.user_root')
                new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                    'name': item['partner_id']['name'],
                    'erp_supplier_id': item['partner_id']['id'],
                    'code': item['partner_id']['code'],
                    'currency_id': 7,
                })
                pinyin_name = pinyin(item['partner_id']['name'], style=Style.NORMAL)
                name = ''.join([syllable[0] for syllable in pinyin_name])
                request.env['res.users'].with_user(admin_user).sudo().create({
                    'name': name,
                    'login': name,
                    'company_ids': [(6, 0, new_company.ids)],
                    'company_id': new_company.id,
                    'password': name,
                })
            return new_company
        try:
            json_data = kwargs.get('data')
            product_configuration = json_data.get('product_configuration', '')
            product_configuration_id = request.env['fast.blank.configuration'].sudo().search(
                [('default_code', '=', json_data.get('product_configuration_id', None))])

            def update_attachment(record, attachment_data, categ_id):
                request.env['ir.attachment'].sudo().create({
                    'name': attachment_data['name'],
                    'datas': attachment_data['datas'],
                    'erp_id': attachment_data['erp_id'],
                    'res_model': record._name,
                    'res_id': record.id,
                    'categ_id': categ_id,
                })
            # 同步工艺单，尺寸表，纸样表
            date = (datetime.datetime.now() + relativedelta(hours=8)).strftime('%Y/%m/%d  %H:%M')
            for process_attr in json_data.get('process_attr_data', []):
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
                update_attachment(product_configuration_id, process_attr, categ_id)
                product_configuration_id.process_attr_last_update_date = date
            for diagram_attr in json_data.get('diagram_attr_data', []):
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
                update_attachment(product_configuration_id, diagram_attr, categ_id)
                product_configuration_id.diagram_attr_last_update_date = date

            for size_attr in json_data.get('size_attr_data', []):
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_size_table').id
                update_attachment(product_configuration_id, size_attr, categ_id)
                product_configuration_id.size_attr_last_update_date = date

            mrp_bom_data = json_data.get('mrp_bom_data', [])
            if mrp_bom_data:
                product_configuration_id.blank_bom.unlink()
            for bom in mrp_bom_data:
                bom_value = {
                    'bank_configuration_id': product_configuration_id.id,
                    'product_tmpl_name': bom.get('product_tmpl_id', ''),
                    'code': bom.get('code', ''),
                    'type': bom.get('type', ''),
                    'product_qty': bom.get('product_qty', ''),
                    'version': bom.get('version', ''),
                }
                bom_detail_list = []
                for bom_detail in bom.get('bom_line_data', []):
                    bom_detail_list.append((0, 0, {
                        'product_name': bom_detail.get('product_id', ''),
                        'body': bom_detail.get('body', ''),
                        'need_qty': bom_detail.get('need_qty', ''),
                        'loss_qty': bom_detail.get('loss_qty', ''),
                        'product_qty': bom_detail.get('product_qty', ''),
                        'product_uom_name': bom_detail.get('product_uom_id', ''),
                        'bom_product_template_attribute_name': str(
                            bom_detail.get('bom_product_value_ids', '')).replace(
                            '[', '').replace(']', ''),
                    }))
                bom_value.update({
                    'blank_bom_detail_line': bom_detail_list
                })
                product_configuration_id.blank_bom.create(bom_value)
            cost_pricing_data = json_data.get('product_cost_pricing_data', [])
            for cost_pricing in cost_pricing_data:
                remove_keys = ['main_material_line', 'sub_material_line', 'secondary_process_line', 'other_fee_line']
                value = {}
                for key in remove_keys:
                    if key in cost_pricing:
                        if key == 'secondary_process_line':
                            process_line = []
                            for line in cost_pricing[key]:
                                new_company_id = find_create_company_user(line)
                                process_line.append((0, 0, {
                                    "currency_id": line['currency_id'],
                                    "name": line['name'],
                                    "company_id": new_company_id.id,
                                    "price": line['price'],
                                    "remark": line['remark'],
                                }))
                        else:
                            value.update({
                                key: self.add_one2many_datas(cost_pricing[key])
                            })
                        cost_pricing.pop(key)
                value.update({
                    'secondary_process_line': process_line
                })
                cost_pricing.update(value)
                cost_pricing.pop('product_configuration_id')
                product_configuration_id.main_material_line.unlink()
                product_configuration_id.sub_material_line.unlink()
                product_configuration_id.secondary_process_line.unlink()
                product_configuration_id.other_fee_line.unlink()
                product_configuration_id.write(cost_pricing)
            product_configuration = json_data.get('product_configuration', '')
            process_price_data = json_data.get('process_price_data') or {}
            process_price_fob_data = []
            process_price_mtp_data = []
            for k, v in process_price_data.items():
                if k == 'process_price_fob_data':
                    product_configuration_id.blank_supplier_quotation_lines.unlink()
                    process_price_fob_data = process_price_data['process_price_fob_data'] or []
                if k == 'process_price_mtp_data':
                    product_configuration_id.blank_processes_supplier_quotation_lines.unlink()
                    process_price_mtp_data = process_price_data['process_price_mtp_data'] or []
            process_price_fob_data_list = []
            def find_create_company_user(item):
                partner_id = item.get('partner_id', False) or ''
                if not partner_id:
                    _logger.error("blank_basics_synchronous 未找到供应商参数")
                    return {
                        'code': 400,
                        'msg': '未找到供应商参数'
                    }
                company_record = request.env['res.company'].search([('code', '=', item['partner_id']['code'])])
                new_company = company_record
                if not company_record:
                    admin_user = request.env.ref('base.user_root')
                    new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                        'name': item['partner_id']['name'],
                        'erp_supplier_id': item['partner_id']['id'],
                        'code': item['partner_id']['code'],
                        'currency_id': 7,
                    })
                    pinyin_name = pinyin(item['partner_id']['name'], style=Style.NORMAL)
                    name = ''.join([syllable[0] for syllable in pinyin_name])
                    request.env['res.users'].with_user(admin_user).sudo().create({
                        'name': name,
                        'login': name,
                        'company_ids': [(6, 0, new_company.ids)],
                        'company_id': new_company.id,
                        'password': name,
                    })
                return new_company
            for item in process_price_fob_data:
                new_company = find_create_company_user(item)
                item.update({'company_id': new_company.id})
                item.pop('partner_id')
                process_price_fob_data_list.append((0, 0, item))
            process_price_mtp_data_list = []
            for item in process_price_mtp_data:
                new_company = find_create_company_user(item)
                item.update({'company_id': new_company.id})
                item.pop('partner_id')
                process_price_mtp_data_list.append((0, 0, item))
            product_configuration_id.write({
                'blank_supplier_quotation_lines': process_price_fob_data_list,
                'blank_processes_supplier_quotation_lines': process_price_mtp_data_list,
            })
            product_configuration_id.write(product_configuration)
        except Exception as e:
            return {
                'code': 400,
                'msg': str(e),
            }
        return {
            'code': 200,
            'msg': 'ok',
        }


    @http.route('/erp/update_company_info', type='json', auth="none", csrf=False, methods=['POST'])
    def update_company_info(self, **kwargs):
        """ 创建公司及用户信息 """
        try:
            json_data = kwargs.get('data')
            company_record = request.env['res.company'].sudo().search([('code', '=', json_data['code'])])
            if not company_record:
                admin_user = request.env.ref('base.user_root')
                new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                    'name': json_data['name'],
                    'erp_supplier_id': json_data['id'],
                    'code': json_data['code'],
                    'currency_id': 7,
                })
                pinyin_name = pinyin(json_data['name'], style=Style.NORMAL)
                name = ''.join([syllable[0] for syllable in pinyin_name])
                request.env['res.users'].with_user(admin_user).sudo().create({
                    'name': name,
                    'login': name,
                    'company_ids': [(6, 0, new_company.ids)],
                    'company_id': new_company.id,
                    'password': name,
                })
            code = 200
            message = '更新成功'
        except Exception as e:
            code = 200
            message = f'更新失败 {e}'
        return {
            'code': code,
            'msg': message
        }


    @http.route('/erp/blank_basics_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_basics_synchronous(self, **kwargs):
        """ 供应商协同端基础信息同步 """
        try:
            def update_attachment(record, attachment_data, categ_id):
                request.env['ir.attachment'].sudo().create({
                    'name': attachment_data['name'],
                    'datas': attachment_data['datas'],
                    'erp_id': attachment_data['erp_id'],
                    'res_model': record._name,
                    'res_id': record.id,
                    'categ_id': categ_id,
                })
            def find_create_company_user(item):
                partner_id = item.get('partner_id', False) or ''
                if not partner_id:
                    _logger.error("blank_basics_synchronous 未找到供应商参数")
                    return {
                        'code': 400,
                        'msg': '未找到供应商参数'
                    }
                company_record = request.env['res.company'].search([('code', '=', partner_id['code'])])
                admin_user = request.env.ref('base.user_root')
                if not company_record:
                    new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                        'name': item['partner_id']['name'],
                        'erp_supplier_id': item['partner_id']['id'],
                        'code': item['partner_id']['code'],
                        'currency_id': 7,
                    })
                    pinyin_name = pinyin(item['partner_id']['name'], style=Style.NORMAL)
                    name = ''.join([syllable[0] for syllable in pinyin_name])
                    request.env['res.users'].with_user(admin_user).sudo().create({
                        'name': name,
                        'login': name,
                        'company_ids': [(6, 0, new_company.ids)],
                        'company_id': new_company.id,
                        'password': name,
                    })
                else:
                    company_record.with_user(admin_user).sudo().code = partner_id['code']
                    new_company = company_record
                return new_company
            json_data = kwargs.get('data', {}) or {}
            product_configuration = json_data.get('product_configuration', '')
            default_code = product_configuration.get('default_code', '')
            process_attachment = product_configuration.get('process_attr_data', False)
            diagram_attachment = product_configuration.get('diagram_attr_data', False)
            size_attachment = product_configuration.get('size_attr_data', False)
            if not default_code:
                raise OdooCustomHTTPException(400, '请传入 default_code 参数')
            blank_basics = request.env['fast.blank.configuration'].sudo()
            record = blank_basics.search([('default_code', '=', default_code)])
            remove_keys = ['process_attr_data', 'diagram_attr_data', 'size_attr_data']
            for key in remove_keys:
                product_configuration.pop(key) if key in product_configuration else False

            if not record:
                record = record.create(product_configuration)
            else:
                record.write(product_configuration)

            if process_attachment:
                record.process_attr_line.unlink()
            if diagram_attachment:
                record.diagram_attr_line.unlink()
            if size_attachment:
                record.size_attr_line.unlink()
            for item in process_attachment:
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
                update_attachment(record, item, categ_id)
            for item in diagram_attachment:
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
                update_attachment(record, item, categ_id)
            for item in size_attachment:
                categ_id = request.env.ref('fast_attachment.ir_attachment_category_size_table').id
                update_attachment(record, item, categ_id)

            # BOM 同步
            mrp_bom_data = json_data.get('mrp_bom_data', [])
            if mrp_bom_data:
                record.blank_bom.unlink()
            for bom in mrp_bom_data:
                bom_value = {
                    'bank_configuration_id': record.id,
                    'product_tmpl_name': bom.get('product_tmpl_id', ''),
                    'code': bom.get('code', ''),
                    'type': bom.get('type', ''),
                    'product_qty': bom.get('product_qty', ''),
                    'version': bom.get('version', ''),
                }
                bom_detail_list = []
                for bom_detail in bom.get('bom_line_data', []):
                    bom_detail_list.append((0, 0, {
                        'product_name': bom_detail.get('product_id', ''),
                        'body': bom_detail.get('body', ''),
                        'need_qty': bom_detail.get('need_qty', ''),
                        'loss_qty': bom_detail.get('loss_qty', ''),
                        'product_qty': bom_detail.get('product_qty', ''),
                        'product_uom_name': bom_detail.get('product_uom_id', ''),
                        'bom_product_template_attribute_name': str(bom_detail.get('bom_product_value_ids', '')).replace(
                            '[', '').replace(']', ''),
                    }))
                bom_value.update({
                    'blank_bom_detail_line': bom_detail_list
                })
                record.blank_bom.create(bom_value)

            # BOM 成本同步
            cost_pricing_data = json_data.get('product_cost_pricing_data', [])
            for cost_pricing in cost_pricing_data:
                remove_keys = ['main_material_line', 'sub_material_line', 'secondary_process_line', 'other_fee_line']
                value = {}
                for key in remove_keys:
                    if key in cost_pricing:
                        if key == 'secondary_process_line':
                            process_line = []
                            for line in cost_pricing[key]:
                                new_company_id = find_create_company_user(line)
                                process_line.append((0,0, {
                                      "currency_id":line['currency_id'],
                                      "name": line['name'],
                                      "company_id":new_company_id.id,
                                      "price": line['price'],
                                      "remark": line['remark'],
                                    }))
                        else:
                            value.update({
                                key: self.add_one2many_datas(cost_pricing[key])
                            })
                        cost_pricing.pop(key)
                value.update({
                    'secondary_process_line': process_line
                })
                cost_pricing.pop('product_configuration_id')
                cost_pricing.update(value)
                record.main_material_line.unlink()
                record.sub_material_line.unlink()
                record.secondary_process_line.unlink()
                record.other_fee_line.unlink()
                record.write(cost_pricing)

                print(cost_pricing_data)

            # 供应商同步
            partner_data = json_data.get('partner_data') or []
            # res_partner_ids = []
            for item in partner_data:
                admin_user = request.env.ref('base.user_root')
                conpany_res = request.env['res.company'].search([('code', '=', item['code'])])
                if conpany_res:
                    conpany_res.with_user(admin_user).sudo().code = item['code']
                    record.write({'company_ids': [(4, conpany_res.id)]})
                else:
                    if not conpany_res:
                        new_company = request.env['res.company'].with_user(admin_user).sudo().create({
                            'name': item['name'],
                            'erp_supplier_id': item['id'],
                            'code': item['code'],
                            'currency_id': 7,
                        })
                        pinyin_name = pinyin(item['name'], style=Style.NORMAL)
                        name = ''.join([syllable[0] for syllable in pinyin_name])
                        request.env['res.users'].with_user(admin_user).sudo().create({
                            'name': name,
                            'login': name,
                            'company_ids': [(6, 0, new_company.ids)],
                            'company_id': new_company.id,
                            'password': name,
                        })
                        record.write({'company_ids': [(4, new_company.id)]})

            #     res_partner = request.env['res.partner'].sudo().search(
            #         ['|', ('name', '=', item['name']), ('erp_partner_id', '=', item['id'])])
            #     if res_partner:
            #         value = {'name': item['name'], 'erp_partner_id': item['id']}
            #         res_partner.write(value)
            #         res_partner_ids.append(res_partner.id)
            #     else:
            #         value = {
            #             'erp_partner_id': item['id'],
            #             'name': item['name']
            #         }
            #         res = res_partner.create(value)
            #         res_partner_ids.append(res.id)
            # record.write({'partner_ids': [(6, 0, res_partner_ids)]})

            # 供应商报价同步
            process_price_data = json_data.get('process_price_data') or {}
            process_price_fob_data = []
            process_price_mtp_data = []
            for k, v in process_price_data.items():
                if k == 'process_price_fob_data':
                    record.blank_supplier_quotation_lines.unlink()
                    process_price_fob_data = process_price_data['process_price_fob_data'] or []
                if k == 'process_price_mtp_data':
                    record.blank_processes_supplier_quotation_lines.unlink()
                    process_price_mtp_data = process_price_data['process_price_mtp_data'] or []
            process_price_fob_data_list = []


            for item in process_price_fob_data:
                new_company = find_create_company_user(item)
                item.update({'company_id': new_company.id})
                item.pop('partner_id')
                process_price_fob_data_list.append((0, 0, item))
            process_price_mtp_data_list = []
            for item in process_price_mtp_data:
                new_company = find_create_company_user(item)
                item.update({'company_id': new_company.id})
                item.pop('partner_id')
                process_price_mtp_data_list.append((0, 0, item))
            record.write({
                'blank_supplier_quotation_lines': process_price_fob_data_list,
                'blank_processes_supplier_quotation_lines': process_price_mtp_data_list,
            })

            message = '同步成功'
            code = 200
        except Exception as e:
            _logger.error(traceback.format_exc())
            message = f'同步失败 {e}'
            code = 400
        return {
            'code': 200,
            'msg': message
        }

    @http.route('/erp/blank_order_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 """
        try:
            json_data = kwargs.get('data')
            partner_data = json_data.get('partner_data')
            json_data = json_data.get('blank_order_data')
            name = json_data.get('name', '')
            # # remove_keys = ['blank_order_detail_line', 'main_material_order_line', 'sub_material_order_line', 'partner_price_line']
            # remove_keys = ['blank_order_detail_line', 'partner_price_line']
            # value = {}
            # for key in remove_keys:
            #     if key in json_data:
            #         value.update({
            #             key: self.add_one2many_datas(json_data[key])
            #         })
            #         json_data.pop(key)
            # json_data.update(value)

            if not name:
                raise OdooCustomHTTPException(400, '请传入 name 参数')
            company_id = request.env['res.company'].search([('code', '=', partner_data[0]['code'])])
            if not company_id:
                _logger.error("blank_order_synchronous 公司不存在")
                return {
                    'code': 400,
                    'msg': '供应商不存在'
                }
            blank_basics = request.env['fast.supplier.order.blank'].sudo()
            record = blank_basics.search([('name', '=', name)])
            record_val = {
                'name': json_data.get('name', ''),  # 订单号
                'type': json_data.get('type'),  # 加工类型
                'order_date': json_data.get('order_date'),  # 下单日期
                'order_type': json_data.get('blank_order_type'),  # 订单类型
                'processing_plant': json_data.get('processing_plant')['name'] if json_data.get('processing_plant') else '',  # 加工厂
                'order_quantity': json_data.get('order_quantity', 0),  # 订单数量
                'completed_quantity': json_data.get('completed_quantity', 0),  # 已完成数量
                'unfinished_quantity': json_data.get('unfinished_quantity'),  # 待完成数量
                'state': json_data.get('state'),  # 加工类型
                'partner_price_line': [],  # 相关费用
                'blank_order_detail_line': [],  # 相关明细
                'company_id': company_id.id,  # 所属公司
            }

            # 相关费用
            partner_price_line = []
            for partner_price_record in json_data.get('partner_price_line', []):
                partner_price_line.append((0, 0, partner_price_record))
            record_val.update({'partner_price_line': partner_price_line})


            # 相关明细
            blank_order_detail_line = []
            for blank_order_detail_record in json_data.get('blank_order_detail_line', []):
                blank_order_detail_line.append((0, 0, {
                    'name': blank_order_detail_record['name'] or '',
                    'product_color_name': blank_order_detail_record['product_color_name'] or '',
                    'product_name': blank_order_detail_record['product_default_code'] or '',
                    'style_name': blank_order_detail_record['product_default_name'] or '',
                    'order_quantity': blank_order_detail_record['order_quantity'],
                    'date_planned': blank_order_detail_record['date_planned'] or '',  # 要求交期
                }))
            record_val.update({'blank_order_detail_line': blank_order_detail_line})

            if not record:
                record.create(record_val)
            else:
                record.blank_order_detail_line.unlink()
                # record.main_material_order_line.unlink()
                # record.sub_material_order_line.unlink()
                record.partner_price_line.unlink()
                record.write(record_val)
            message = '同步成功'
            code = 200
            print(json_data)
        except Exception as e:
            _logger.error(traceback.format_exc())
            message = f'同步失败 {e}'
            code = 400
        return {
            'code': code,
            'msg': message
        }

    @http.route('/erp/blank_order_material_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_material_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 主辅料同步 """
        try:
            json_data = json.loads(request.httprequest.data)
            po = json_data['po_order_blank']
            main_material_order_line_data = json_data['main_material_order_line_data']
            blank_basics_record = request.env['fast.supplier.order.blank'].sudo().search([('name', '=', po)])
            if main_material_order_line_data:
                blank_basics_record.main_material_order_line.unlink()
            values = []
            for item in main_material_order_line_data:
                value = {
                    # 'outsource_order_blank_id': blank_basics_record.id,
                    'conf_type': item['conf_type'],
                    'product_default_code': item.get('product_default_code', ''),
                    'product_default_name': item.get('product_default_name', ''),
                    'color_value_name': item.get('color_value_id', ''),
                    'color_cn_name': item.get('color_cn_name', ''),
                    'categ_name': item.get('categ_id')[0] or '',
                    'product_qty': item.get('product_qty', ''),
                    'apply_qty': item.get('apply_qty', ''),
                    'ship_qty': item.get('ship_qty', ''),
                    'return_qty': item.get('return_qty', ''),
                    'body': item.get('body', ''),
                }
                values.append((0, 0, value))
            if blank_basics_record:
                blank_basics_record.write({'main_material_order_line': values})

            sub_material_order_line_data = json_data['sub_material_order_line_data']
            if sub_material_order_line_data:
                blank_basics_record.sub_material_order_line.unlink()
            values = []
            for item in sub_material_order_line_data:
                value = {
                    # 'outsource_order_blank_id': blank_basics_record.id,
                    'conf_type': item['conf_type'],
                    'product_default_code': item.get('product_default_code', ''),
                    'product_default_name': item.get('product_default_name', ''),
                    'color_value_name': item.get('color_value_id', ''),
                    'color_cn_name': item.get('color_cn_name', ''),
                    'categ_name': item.get('categ_id')[0] or '',
                    'product_qty': item.get('product_qty', ''),
                    'apply_qty': item.get('apply_qty', ''),
                    'ship_qty': item.get('ship_qty', ''),
                    'return_qty': item.get('return_qty', ''),
                    'body': item.get('body', ''),
                    'product_spec_name': item.get('product_spec_id', ''),
                    'product_spec_remark': item.get('product_spec_remark', ''),
                }
                values.append((0, 0, value))
            if blank_basics_record:
                blank_basics_record.write({'sub_material_order_line': values})
            # blank_basics_record = request.env['fast.supplier.order.blank'].sudo().search([('name', '=', po)])
            # conf_type = json_data['conf_type']
            # product_id = json_data['product_id']
            # blank_basics_record = request.env['fast.supplier.order.blank'].sudo().search([('name', '=', po)])
            # material_requirements_record = request.env['fast.blank.order.material.requirements'].sudo().search([('product_id', '=', product_id)])
            # value = {
            #     'outsource_order_blank_id': blank_basics_record.id,
            #     'product_id': json_data['product_id'],
            #     'conf_type': conf_type,
            #     'product_default_code': json_data.get('origin_product_configuration_ids', ''),
            #     'product_default_name': json_data.get('origin_product_configuration_name', ''),
            #     'color_value_name': json_data.get('color_value_id', ''),
            #     'color_cn_name': json_data.get('color_value_name', ''),
            #     'categ_name': json_data.get('categ_id')[0] or '',
            #     'product_qty': json_data.get('product_qty', ''),
            #
            #     'apply_qty': json_data.get('apply_qty', ''),
            #     'ship_qty': json_data.get('ship_qty', ''),
            #     'return_qty': json_data.get('return_qty', ''),
            #     'body': json_data.get('body', ''),
            # }
            # if conf_type == 'sub':
            #     value.update({
            #             'product_spec_name': json_data.get('product_spec_name', ''),
            #             'product_spec_remark': json_data.get('product_spec_remark', ''),
            #     })
            #
            # if not blank_basics_record:
            #     raise OdooCustomHTTPException(400, '供应商未找到该订单！')
            # else:
            #     if material_requirements_record:
            #         material_requirements_record.write(value)
            #     else:
            #         material_requirements_record.create(value)

            message = '同步成功'
            code = 200
            print(json_data)
        except Exception as e:
            code = 400
            message = f'同步失败 {e}'
        return {
            'code': code,
            'msg': message
        }

    @http.route('/erp/blank_order_onchange_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_onchange_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 变更同步 """
        try:
            json_data = kwargs.get('data')
            blank_order_return_data = json_data.get('blank_order_return_data', [])
            po = json_data.get('po', False)
            for blank_order_return in blank_order_return_data:
                domain = []
                if po:
                    domain.append(('po_name', '=', po))
                domain.append(('product_name', '=', blank_order_return['product_id']))
                return_record = request.env['fast.blank_order_detail'].sudo().search(domain)
                if return_record:
                    return_record.change_quantity = f"-{blank_order_return['product_qty']}"
                    return_record.order_quantity -= int(blank_order_return['product_qty'])
                    return_record.unfinished_quantity = return_record.order_quantity - int(blank_order_return['done_qty'])
                    return_record.blank_order_id.last_change_date = (datetime.datetime.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
                else:
                    return {
                        'code': 400,
                        'message': f"未找到 po = {po}, product_name = {str(blank_order_return['product_id'])}"
                    }
            code = 400
            message = f'同步成功'
        except Exception as e:
            _logger.error(traceback.format_exc())
            code = 400
            message = f'同步失败 {e}'
        return {
            'code': code,
            'msg': message
        }

    @http.route('/erp/sync_blank_difference', type='json', auth='none', csrf=False, methods=['POST'])
    def sync_blank_difference(self,**kwargs):
        """ 供应商协同端 空白版差异同步（已收货数量） """
        try:
            json_data = kwargs.get('data', {})
            if not json_data.get('box_number', False):
                raise UserError('请传入 box_number 参数')
            packing_list_detail_record = request.env['fast.blank.packing_list_detail'].search(
                [('box_number', '=', json_data['box_number'])])
            size_list = json_data.get('size_list', False)
            if not size_list:
                raise UserError('请传入 size_list 参数')
            for size in size_list:
                packing_list_detail_record.filtered(lambda x: x.size == size['size_name']).write(
                    {'received_quantity': int(size['product_qty'])})
            return {
                'code': 200,
                'msg': '更新成功',
            }
        except Exception as e:
            return {
                'code': 400,
                'msg': f'同步失败 {e}'
            }

    @http.route('/erp/blank_order_process_cost_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_process_cost_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 加工费用 """
        json_data = kwargs.get('data',[])
        for item in json_data:
            order_record = request.env['fast.supplier.order.blank'].sudo().search([('name', '=', item['po'])])
            order_record.partner_price_line.filtered(lambda x: x.name == item['product_configuration_id']).unlink()
            partner_price = [(0, 0, {
                'name': item['product_configuration_id'] or '',
                'process_price': item['process_price'] or 0,
                'management_price': item['management_price'] or 0,
                'other_price': item['other_price'] or 0,
                'price': item['total_price'] or 0,
                'bom_price': item['bom_price'] or 0,
                'total_price': item['total_price'] or 0,
                'remark': item['remark'],
            })]
            order_record.partner_price_line = partner_price
        return {
            'code': 200,
            'msg': '更新成功',
        }

    @http.route('/aes_encrypt_content', type='http', auth="none", csrf=False, methods=['GET'])
    def aes_encrypt_content(self, josn_data={}):
        AES_KEY_STRING = b'ByPAxevz3uiGIRRQ'
        now_time = str(int(time.time()))

        uid_bytes = self.encrypt_aes(f"admin {now_time}", AES_KEY_STRING)
        upwd_bytes = self.encrypt_aes(f"kFwGbMM1GVovfn7Q {now_time}", AES_KEY_STRING)

        uid_message = base64.b64encode(uid_bytes).decode('utf-8')
        upwd_message = base64.b64encode(upwd_bytes).decode('utf-8')

        uid = self.bytes_to_hex(uid_message.encode('utf-8'))
        upwd = self.bytes_to_hex(upwd_message.encode('utf-8'))

        self.login_check(uid, upwd)

        print("uid:", uid)
        print("upwd:", upwd)

    def login_check(self, uid=False, upwd=False):
        now_time = str(int(datetime.datetime.now().timestamp()))
        # 使用固定的128位AES密钥
        aes_key_string = "ByPAxevz3uiGIRRQ"
        aes_key = aes_key_string.encode('utf-8')

        def hex_string_to_str(hex_string):
            hex_bytes = bytes.fromhex(hex_string)
            result_string = hex_bytes.decode('utf-8')
            return result_string

        def decrypt_aes(encrypted_message, key):
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted_bytes = unpad(cipher.decrypt(encrypted_message), AES.block_size)
            return decrypted_bytes

        uid = hex_string_to_str(uid)
        upwd = hex_string_to_str(upwd)
        # 将Base64字符串转换为字节码
        uid_encrypted_message = base64.b64decode(uid)
        upwd_encrypted_message = base64.b64decode(upwd)

        # 使用AES密钥解密消息
        uid_decrypted_message = decrypt_aes(uid_encrypted_message, aes_key)
        upwd_decrypted_message = decrypt_aes(upwd_encrypted_message, aes_key)

        uid_message = uid_decrypted_message.decode('utf-8')
        upwd_message = upwd_decrypted_message.decode('utf-8')
        receipt_time = uid_message.split(' ')[1]
        # 对接接口过期时长 接收请求前后1小时
        if not (receipt_time and ((int(now_time) - 600) < int(receipt_time) < (int(now_time) + 600))):
            raise OdooCustomHTTPException(401, 'Session expired')

        login_user = uid_message.split(' ')[0]
        password = upwd_message.split(' ')[0]
        opener = self.get_cookie(login_user, password)
        if type(opener) == str and 'Session expired' in opener:
            # raise OdooCustomHTTPException(401, opener)
            raise http.SessionExpiredException("Session expired")
        return opener

    # def get_cookie(self, login_user, password):
    #     """ 模拟登录 获取 cookies """
    #     global Opener
    #     data = {
    #         'login': login_user,
    #         'password': password,
    #         'db': db_monodb
    #     }
    #     login = requests.post(url=Base_url + '/web/login', data=data)
    #     opener = requests.Session()
    #     opener.cookies = login.cookies
    #     return opener

    def encrypt_aes(self, message, key):
        cipher = AES.new(key, AES.MODE_ECB)
        padded_message = pad(message.encode('utf-8'), AES.block_size)
        encrypted_bytes = cipher.encrypt(padded_message)
        return encrypted_bytes

    def bytes_to_hex(self, bytes_data):
        return bytes_data.hex()

    # @http.route('/aes_encrypt_content', type='http', auth="none", csrf=False, methods=['GET'])
    # def aes_encrypt_content(self):
    #     AES_KEY_STRING = b'ByPAxevz3uiGIRRQ'
    #     now_time = str(int(time.time()))
    #
    #     uid_bytes = self.encrypt_aes(f"admin {now_time}", AES_KEY_STRING)
    #     upwd_bytes = self.encrypt_aes(f"kFwGbMM1GVovfn7Q {now_time}", AES_KEY_STRING)
    #
    #     uid_message = base64.b64encode(uid_bytes).decode('utf-8')
    #     upwd_message = base64.b64encode(upwd_bytes).decode('utf-8')
    #
    #     uid = self.bytes_to_hex(uid_message.encode('utf-8'))
    #     upwd = self.bytes_to_hex(upwd_message.encode('utf-8'))
    #
    #     self.login_check(uid, upwd)
    #
    #     print("uid:", uid)
    #     print("upwd:", upwd)

    # @http.route('/aes_encrypt_content1', type='http', auth="none", csrf=False, methods=['GET'])
    # def aes_encrypt_content1(self):
    #     AES_KEY_STRING = b'ByPAxevz3uiGIRRQ'
    #
    #     uid_bytes = self.encrypt_aes(f"admin", AES_KEY_STRING)
    #     upwd_bytes = self.encrypt_aes(f"kFwGbMM1GVovfn7Q", AES_KEY_STRING)
    #
    #     uid_message = base64.b64encode(uid_bytes).decode('utf-8')
    #     upwd_message = base64.b64encode(upwd_bytes).decode('utf-8')
    #
    #     uid = self.bytes_to_hex(uid_message.encode('utf-8'))
    #     upwd = self.bytes_to_hex(upwd_message.encode('utf-8'))
    #
    #     print(uid)
    #     print(upwd)

    # @http.route('/supplier/getToken', type='json', auth='none', csrf=False, methods=['POST'])
    # def supplier_getToken(self, **kw):
    #     params = {
    #         'appId': '1636631067746537473',
    #         'secret': '9456bb6ed3882a62340180f83c97eddd'
    #     }
    #     data = requests.get(url=f'{Base_url}/api/tcc-open-platform/open-api/getToken',
    #                         params=params)
    #     if data.status_code == 200:
    #         token = eval(data.content).get('data')['token']
    #     else:
    #         raise OdooCustomHTTPException(data.status_code, data.content)
    #     return token
