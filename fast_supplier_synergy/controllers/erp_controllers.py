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

_logger = logging.getLogger(__name__)

Opener = False

db_monodb = False
all_dbs = http.db_list(force=True)
if len(all_dbs) == 1:
    db_monodb = all_dbs[0]

if sys.platform == 'linux':
    Base_url = 'http://127.0.0.1:8069'
else:
    Base_url = 'http://127.0.0.1:8011'

Dev_url = 'http://192.168.6.50:10010'

BlankSize = ['xxs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'os', '2t', '3t', '4t', '4', '5', '6', '7', '8', '8/10', '10/12', '12/14', '14/16', '16', '18/20']


class ErpController(http.Controller):

    def add_one2many_datas(self, datas_list):
        datas = []
        for item in datas_list:
            datas.append((0, 0, item))
        return datas

    @http.route(['/erp/update_company_info'], type='json', auto='none', csrf=False, methods=['POST'])
    def update_company_info(self):
        """ 更新公司信息 """
        json_data = json.loads(request.httprequest.data)
        print(json_data)

        # 公司同步
        # res_company_ids = []
        # for item in partner_data:
        #     res_company = request.env['res.company'].sudo().search([('erp_supplier_id', '=', item['id'])])
        #     if res_company:
        #         value = {'name': item['name']}
        #         res_company.write(value)
        #         res_company_ids.append(res_company.id)
        #     else:
        #         value = {
        #             'erp_supplier_id': item['id'],
        #             'name': item['name']
        #         }
        #         res = res_company.create(value)
        #         res_company_ids.append(res.id)
        # record.write({'company_ids': [(6, 0, res_company_ids)]})


    @http.route('/erp/blank_basics_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_basics_synchronous(self, **kwargs):
        """ 供应商协同端基础信息同步 """
        def update_attachment(record, attachment_data, categ_id):
            request.env['ir.attachment'].sudo().create({
                'name': attachment_data['name'],
                'datas': attachment_data['datas'],
                'res_model': record._name,
                'res_id': record.id,
                'categ_id': categ_id,
            })
        try:
            json_data = json.loads(request.httprequest.data)
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
                        'bom_product_template_attribute_name': str(bom_detail.get('bom_product_value_ids', '')).replace('[', '').replace(']', ''),
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
                        value.update({
                            key: self.add_one2many_datas(cost_pricing[key])
                        })
                        cost_pricing.pop(key)
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
            res_partner_ids = []
            for item in partner_data:
                res_partner = request.env['res.partner'].sudo().search([('erp_partner_id', '=', item['id'])])
                if res_partner:
                    value = {'name': item['name']}
                    res_partner.write(value)
                    res_partner_ids.append(res_partner.id)
                else:
                    value = {
                        'erp_partner_id': item['id'],
                        'name': item['name']
                    }
                    res = res_partner.create(value)
                    res_partner_ids.append(res.id)
            record.write({'partner_ids': [(6, 0, res_partner_ids)]})

            message = '同步成功'
        except Exception as e:
            _logger.error(traceback.format_exc())
            message = f'同步失败 {e}'
        return {
            'code': 200,
            'message': message
        }

    @http.route('/erp/blank_order_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 """
        try:
            json_data = json.loads(request.httprequest.data)
            name = json_data.get('name', '')
            # remove_keys = ['blank_order_detail_line', 'main_material_order_line', 'sub_material_order_line', 'partner_price_line']
            remove_keys = ['blank_order_detail_line', 'partner_price_line']

            value = {}
            for key in remove_keys:
                if key in json_data:
                    value.update({
                        key: self.add_one2many_datas(json_data[key])
                    })
                    json_data.pop(key)

            json_data.update(value)
            if not name:
                raise OdooCustomHTTPException(400, '请传入 name 参数')
            blank_basics = request.env['fast.supplier.order.blank'].sudo()
            record = blank_basics.search([('name', '=', name)])
            if not record:
                record.create(json_data)
            else:
                record.blank_order_detail_line.unlink()
                # record.main_material_order_line.unlink()
                # record.sub_material_order_line.unlink()
                record.partner_price_line.unlink()
                record.write(json_data)
            message = '同步成功'
            print(json_data)
        except Exception as e:
            message = f'同步失败 {e}'
        return {
            'code': 200,
            'message': message
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
            print(json_data)
        except Exception as e:
            message = f'同步失败 {e}'
        return {
            'code': 200,
            'message': message
        }


    @http.route('/erp/blank_order_onchange_synchronous', type='json', auth="none", csrf=False, methods=['POST'])
    def blank_order_onchange_synchronous(self, **kwargs):
        """ 供应商协同端 订单同步 变更同步 """
        json_data = json.loads(request.httprequest.data)
        blank_order_return_data = json_data.get('blank_order_return_data', [])
        po = json_data.get('po', False)
        for blank_order_return in blank_order_return_data:
            domain = []
            if po:
                domain.append(('po_name', '=', po))
            domain.append(('product_name', '=', blank_order_return['product_id']))
            return_record = request.env['fast.blank_order_detail'].sudo().search(domain)
            if return_record:
                change_quantity = blank_order_return['product_qty'] - blank_order_return['un_done_qty']
                return_record.change_quantity = str(change_quantity)
                if change_quantity > 0:
                    return_record.change_quantity = f"-{blank_order_return['product_qty'] + change_quantity}"
                if not change_quantity:
                    return_record.change_quantity = f"-{str(blank_order_return['product_qty'])}"
            else:
                return {
                    'code': 400,
                    'message': f"未找到 po = {po}, product_name = {str(blank_order_return['product_id'])}"
                }
        return {
            'code': 200,
            'message': f'更新成功'
        }

    @http.route('/erp/sync_blank_difference', type='json', auth='none', csrf=False, methods=['POST'])
    def sync_blank_difference(self):
        """ 供应商协同端 空白版差异同步（已收货数量） """
        json_data = json.loads(request.httprequest.data)
        if not json_data.get('box_number', False):
            raise UserError('请传入 box_number 参数')
        packing_list_detail_record = request.env['fast.blank.packing_list_detail'].search([('box_number', '=', json_data['box_number'])])
        size_list = json_data.get('size_list', False)
        if not size_list:
            raise UserError('请传入 size_list 参数')
        for size in size_list:
            if size['product_qty']:
                packing_list_detail_record.write({'received_quantity': int(size['product_qty'])})
                break
        return {
            'code': 200,
            'message': '更新成功',
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

    def get_cookie(self, login_user, password):
        """ 模拟登录 获取 cookies """
        global Opener
        data = {
            'login': login_user,
            'password': password,
            'db': db_monodb
        }
        login = requests.post(url=Base_url + '/web/login', data=data)
        opener = requests.Session()
        opener.cookies = login.cookies
        return opener


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