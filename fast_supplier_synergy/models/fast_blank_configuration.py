# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
import requests
import traceback
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

PRICE_DIGITS = 'Product Price'
FLOAT_DIGITS = 'Product Unit of Measure'


class FastBlankConfiguration(models.Model):
    _name = 'fast.blank.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '空白版基础资料'
    _order = 'write_date desc, id desc'
    _rec_name = 'default_code'

    def diagram_attr_count_domain(self):
        """纸样"""
        if self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
            return [('categ_id', '=', categ_id)]

    def process_attr_domain(self):
        """工艺单"""
        if self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
            return [('categ_id', '=', categ_id)]

    def size_attr_domain(self):
        """尺寸表"""
        if self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_size_table').id
            return [('categ_id', '=', categ_id)]

    erp_id = fields.Integer('erp_id')
    partner_ids = fields.Many2many('res.partner', relation='fast_blank_configuration_res_partnere_rel',
                                   column1='blank_configuration_id', column2='partner_id', string='所属供应商联系人')
    company_ids = fields.Many2many('res.company', relation='fast_blank_configuration_res_company_rel',
                                   column1='blank_configuration_id', column2='company_id', string='相关公司')
    company_id = fields.Many2one('res.company', string='所属公司')
    default_code = fields.Char('产品编码', copy=True, store=1)
    name = fields.Char('产品名称', copy=True)
    image_1920 = fields.Image('图片', copy=False)
    is_print_patterns = fields.Boolean('是否印花', default=False)
    categ_name = fields.Char('产品类别', copy=True)
    assist_uom_name = fields.Char('计量单位', copy=True)
    main_product_configuration_name = fields.Char('主身面料', copy=True)
    diagram_attr_line = fields.One2many('ir.attachment', 'res_id', domain=diagram_attr_count_domain, string='纸样')
    process_attr_line = fields.One2many('ir.attachment', 'res_id', domain=process_attr_domain, string='工艺单')
    size_attr_line = fields.One2many('ir.attachment', 'res_id', domain=size_attr_domain, string='尺寸表')

    diagram_attr_count = fields.Integer('纸样', compute='_compute_diagram_attr_count')
    process_attr_count = fields.Integer('工艺单', compute='_compute_process_attr_count')
    size_attr_count = fields.Integer('尺寸表', compute='_compute_size_attr_count')

    diagram_attr_last_update_date = fields.Char('纸样最后变更时间')
    process_attr_last_update_date = fields.Char('工艺单最后变更时间')
    size_attr_last_update_date = fields.Char('尺寸表最后变更时间')

    # fast_blank_configuration_last_update_date = fields.Char('最后更新时间',compute='_get_fast_blank_configuration_last_update_date')
    #
    # def  _get_fast_blank_configuration_last_update_date(self):
    #     for item in self:
    #         update_set = [item.diagram_attr_last_update_date,item.process_attr_last_update_date,item.size_attr_last_update_date]
    #         item.fast_blank_configuration_last_update_date = sorted(update_set)[0]

    last_update_date = fields.Char('最后更新时间', compute='_compute_update_date', store=True)

    bom_count = fields.Integer('BOM', compute='_compute_bom_count')
    blank_bom = fields.One2many('fast.blank.bom', 'bank_configuration_id', string='相关BOM')

    # 成本
    product_tmpl_id = fields.Char('颜色')
    product_id = fields.Char('尺码')
    untaxed_amount = fields.Float('成本合计', digits=(16, 4))
    remark = fields.Text('备注')
    fob_mtp_quotation_state_show = fields.Text('供应商报价状态', compute='_compute_fob_mtp_quotation_state_show')
    fob_mtp_quotation_state = fields.Char('供应商FOB|MTP报价状态code', compute='_compute_fob_mtp_quotation_state_show')

    main_material_line = fields.One2many('fast.product.cost.pricing.material', 'bank_configuration_id', '物料成本-主料',
                                         domain=[('conf_type', '=', 'main')])
    sub_material_line = fields.One2many('fast.product.cost.pricing.material', 'bank_configuration_id', '物料成本-辅料',
                                        domain=[('conf_type', '=', 'sub')])
    secondary_process_line = fields.One2many('fast.product.cost.pricing.secondary.process', 'bank_configuration_id',
                                             '二次工艺费用')
    other_fee_line = fields.One2many('fast.product.cost.pricing.other.fee', 'bank_configuration_id', '其它费用')
    # 空白版供应商报价
    blank_supplier_quotation_lines = fields.One2many('fast.overall.outsourcing.supplier.quotation',
                                                     'product_configuration_id', string='空白版供应商FOB报价')
    # 空白版工序报价
    blank_processes_supplier_quotation_lines = fields.One2many('fast.production.processes.supplier.quotation',
                                                               'product_configuration_id', string='空白版供应商MTP报价')

    @api.depends('diagram_attr_last_update_date','process_attr_last_update_date','size_attr_last_update_date')
    def _compute_update_date(self):
        for record in self:
            list = []
            if record.diagram_attr_last_update_date:
                list.append(record.diagram_attr_last_update_date)
            if record.process_attr_last_update_date:
                list.append(record.process_attr_last_update_date)
            if record.size_attr_last_update_date:
                list.append(record.size_attr_last_update_date)
            record.last_update_date = max(list) if list else False

    def _compute_fob_mtp_quotation_state_show(self):
        for order in self:
            # self.env.user.user_has_groups('fast_supplier_synergy.fast_blank_configuration_user_self')
            fob_count = len(order.blank_supplier_quotation_lines)
            mtp_count = len(order.blank_processes_supplier_quotation_lines)
            if fob_count > 0 or mtp_count > 0:
                if fob_count > 0:
                    fob_info = f"FOB报价{fob_count}项"
                else:
                    fob_info = 'FOB未报价'
                if mtp_count > 0:
                    mtp_info = f"MTP报价{mtp_count}项"
                else:
                    mtp_info = 'MTP未报价'
                if fob_count > 0 and mtp_count > 0:
                    fob_mtp_quotation_state = 'price_quoted'  # 已报价
                else:
                    fob_mtp_quotation_state = 'price_part_quoted'  # 部分报价
                fob_mtp_quotation_state_show = '\n'.join([fob_info, mtp_info])
            else:
                fob_mtp_quotation_state = 'not_price'
                fob_mtp_quotation_state_show = '未报价'
            order.fob_mtp_quotation_state = fob_mtp_quotation_state
            order.fob_mtp_quotation_state_show = fob_mtp_quotation_state_show

    # 打开供应商报价
    def action_open_fast_supplier_quotation_main_action(self):
        self.ensure_one()
        action = self.env.ref('fast_supplier_synergy.action_fast_supplier_quotation').sudo().read()[0]
        form_id = self.env.ref('fast_supplier_synergy.fast_supplier_quotation_form', False)
        action['views'] = [(form_id and form_id.id or False, 'form')]
        action['res_id'] = self.id
        action['target'] = 'new'
        action['context'] = {'dialog_size': 'extra-modal-max-85'}
        action['display_name'] = f"{self.display_name} 报价"
        action['name'] = f"{self.display_name} 报价"
        return action

    # 计算BOM数量
    def _compute_bom_count(self):
        for order in self:
            order.bom_count = self.env['fast.blank.bom'].search_count([('bank_configuration_id', '=', order.id)])

    def action_view_bom(self):
        """
        FORM 查看 BOM
        :return:
        """
        action = self.env["ir.actions.actions"]._for_xml_id("fast_supplier_synergy.product_open_bom")
        # bank_configuration_records = self.env['fast.blank.bom'].search([('bank_configuration_id', '=', self.id)])
        # action['domain'] = [('id', 'in', bank_configuration_records.ids)]
        action['domain'] = [('bank_configuration_id', '=', self.id)]
        return action

    # 纸样附件
    def _compute_diagram_attr_count(self):
        for order in self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
            order.diagram_attr_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', order._name), ('res_id', '=', order.id), ('categ_id', 'child_of', categ_id)])

    # 工艺单附件
    def _compute_process_attr_count(self):
        for order in self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
            order.process_attr_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', order._name), ('res_id', '=', order.id), ('categ_id', 'child_of', categ_id)])

    # 尺寸表附件
    def _compute_size_attr_count(self):
        for order in self:
            categ_id = self.env.ref('fast_attachment.ir_attachment_category_size_table').id
            order.size_attr_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', order._name), ('res_id', '=', order.id), ('categ_id', 'child_of', categ_id)])

    # 查看纸样附件
    def action_get_attachment_view_diagram(self):
        self.ensure_one()
        action = self._get_attr_action()
        categ_id = self.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
        action['domain'] += [('categ_id', 'child_of', categ_id)]
        action['context']['default_categ_id'] = categ_id
        action['display_name'] = '纸样'
        return action

    # 查看工艺单附件
    def action_get_attachment_view_process(self):
        self.ensure_one()
        action = self._get_attr_action()
        categ_id = self.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
        action['domain'] += [('categ_id', 'child_of', categ_id)]
        action['context']['default_categ_id'] = categ_id
        action['display_name'] = '工艺单'
        return action

    # 查看尺寸表附件
    def action_get_attachment_view_size(self):
        self.ensure_one()
        action = self._get_attr_action()
        categ_id = self.env.ref('fast_attachment.ir_attachment_category_size_table').id
        action['domain'] += [('categ_id', 'child_of', categ_id)]
        action['context']['default_categ_id'] = categ_id
        action['display_name'] = '尺寸表'
        return action

    # 获取附件action
    def _get_attr_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        kanban_id = self.env.ref('fast_attachment.view_document_file_kanban_fast_attachment').id
        action['views'] = [[kanban_id, 'kanban']]
        action['domain'] = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.id
        }
        return action

    @api.model
    def update_basic_data(self, **kwargs):
        """
        更新基础资料数据，每次进入基础信息更新时，同步最新数据
        :param kwargs:
        :return:
        """
        pass
        # try:
        #     id = kwargs.get('id', False)
        #     record = self.search([('id', '=', id)])
        #     try:
        #         Dev_url = self.env['fast.config.dev'].sudo().get_dev_url()
        #         response = requests.get(url=f'{Dev_url}/leda/synchronized_new_product_configuration', params={'default_code': record.default_code}, timeout=10)
        #     except requests.exceptions.RequestException as e:
        #         return {
        #             'code': 500,
        #             'message': f"获取最新数据失败，请稍后再试，如果问题持续出现，请联系管理员！\n {e}"
        #         }
        #     json_data = response.json()
        #
        #     """ 供应商协同端基础信息同步 """
        #
        #     def update_attachment(record, attachment_data, categ_id):
        #         self.env['ir.attachment'].sudo().create({
        #             'name': attachment_data['name'],
        #             'datas': attachment_data['datas'],
        #             'res_model': record._name,
        #             'res_id': record.id,
        #             'categ_id': categ_id,
        #         })
        #
        #     def add_one2many_datas(datas_list):
        #         datas = []
        #         for item in datas_list:
        #             datas.append((0, 0, item))
        #         return datas
        #
        #     product_configuration = json_data.get('product_configuration', '')
        #     default_code = product_configuration.get('default_code', '')
        #     process_attachment = product_configuration.get('process_attr_data', False)
        #     diagram_attachment = product_configuration.get('diagram_attr_data', False)
        #     size_attachment = product_configuration.get('size_attr_data', False)
        #     if not default_code:
        #         raise ValidationError(f'未得到 default_code')
        #     blank_basics = self.env['fast.blank.configuration'].sudo()
        #     record = blank_basics.search([('default_code', '=', default_code)])
        #     remove_keys = ['process_attr_data', 'diagram_attr_data', 'size_attr_data']
        #     for key in remove_keys:
        #         product_configuration.pop(key) if key in product_configuration else False
        #
        #     if not record:
        #         record = record.create(product_configuration)
        #     else:
        #         record.write(product_configuration)
        #
        #     record.process_attr_line.unlink()
        #     record.diagram_attr_line.unlink()
        #     record.size_attr_line.unlink()
        #     for item in process_attachment:
        #         categ_id = self.env.ref('fast_attachment.ir_attachment_category_process_sheet').id
        #         update_attachment(record, item, categ_id)
        #     for item in diagram_attachment:
        #         categ_id = self.env.ref('fast_attachment.ir_attachment_category_frame_diagram').id
        #         update_attachment(record, item, categ_id)
        #     for item in size_attachment:
        #         categ_id = self.env.ref('fast_attachment.ir_attachment_category_size_table').id
        #         update_attachment(record, item, categ_id)
        #
        #     # BOM 同步
        #     mrp_bom_data = json_data.get('mrp_bom_data', [])
        #     if mrp_bom_data:
        #         record.blank_bom.unlink()
        #     for bom in mrp_bom_data:
        #         bom_value = {
        #             'bank_configuration_id': record.id,
        #             'product_tmpl_name': bom.get('product_tmpl_id', ''),
        #             'code': bom.get('code', ''),
        #             'type': bom.get('type', ''),
        #             'product_qty': bom.get('product_qty', ''),
        #             'version': bom.get('version', ''),
        #         }
        #         bom_detail_list = []
        #         for bom_detail in bom.get('bom_line_data', []):
        #             bom_detail_list.append((0, 0, {
        #                 'product_name': bom_detail.get('product_id', ''),
        #                 'body': bom_detail.get('body', ''),
        #                 'need_qty': bom_detail.get('need_qty', ''),
        #                 'loss_qty': bom_detail.get('loss_qty', ''),
        #                 'product_qty': bom_detail.get('product_qty', ''),
        #                 'product_uom_name': bom_detail.get('product_uom_id', ''),
        #                 'bom_product_template_attribute_name': str(
        #                     bom_detail.get('bom_product_value_ids', '')).replace('[', '').replace(']', ''),
        #             }))
        #         bom_value.update({
        #             'blank_bom_detail_line': bom_detail_list
        #         })
        #         record.blank_bom.create(bom_value)
        #
        #     # BOM 成本同步
        #     cost_pricing_data = json_data.get('product_cost_pricing_data', [])
        #     for cost_pricing in cost_pricing_data:
        #         remove_keys = ['main_material_line', 'sub_material_line', 'secondary_process_line',
        #                        'other_fee_line']
        #         value = {}
        #         for key in remove_keys:
        #             if key in cost_pricing:
        #                 value.update({
        #                     key: add_one2many_datas(cost_pricing[key])
        #                 })
        #                 cost_pricing.pop(key)
        #         cost_pricing.pop('product_configuration_id')
        #         cost_pricing.update(value)
        #         record.main_material_line.unlink()
        #         record.sub_material_line.unlink()
        #         record.secondary_process_line.unlink()
        #         record.other_fee_line.unlink()
        #         record.write(cost_pricing)
        #
        #     # 供应商同步
        #     partner_data = json_data.get('partner_data') or []
        #     res_partner_ids = []
        #     for item in partner_data:
        #         res_partner = self.env['res.partner'].sudo().search(
        #             ['|', ('name', '=', item['name']), ('erp_partner_id', '=', item['id'])])
        #         if res_partner:
        #             value = {'name': item['name'], 'erp_partner_id': item['id']}
        #             res_partner.write(value)
        #             res_partner_ids.append(res_partner.id)
        #         else:
        #             value = {
        #                 'erp_partner_id': item['id'],
        #                 'name': item['name']
        #             }
        #             res = res_partner.create(value)
        #             res_partner_ids.append(res.id)
        #     record.write({'partner_ids': [(6, 0, res_partner_ids)]})
        #
        #     # 供应商报价同步
        #     record.blank_supplier_quotation_lines.unlink()
        #     record.blank_processes_supplier_quotation_lines.unlink()
        #     process_price_data = json_data.get('process_price_data') or {}
        #     process_price_fob_data = []
        #     process_price_mtp_data = []
        #     for k, v in process_price_data.items():
        #         if k == 'process_price_fob_data':
        #             process_price_fob_data = process_price_data['process_price_fob_data'] or []
        #         if k == 'process_price_mtp_data':
        #             process_price_mtp_data = process_price_data['process_price_mtp_data'] or []
        #     process_price_fob_data_list = []
        #     for item in process_price_fob_data:
        #         process_price_fob_data_list.append((0, 0, item))
        #     process_price_mtp_data_list = []
        #     for item in process_price_mtp_data:
        #         process_price_mtp_data_list.append((0, 0, item))
        #     record.write({
        #         'blank_supplier_quotation_lines': process_price_fob_data_list,
        #         'blank_processes_supplier_quotation_lines': process_price_mtp_data_list,
        #     })
        #     code = 200
        #     message = '同步成功'
        # except Exception as e:
        #     code = 500
        #     message = f'同步失败，请联系管理员！\n {e}'
        #     _logger.info(traceback.format_exc())
        # return {
        #     'code': code,
        #     'message': message
        # }


class FastBlankBom(models.Model):
    _name = 'fast.blank.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '空白版BOM'

    erp_id = fields.Integer('erp_id')
    bank_configuration_id = fields.Many2one('fast.blank.configuration', string='所属空白版', ondelete='cascade')
    blank_bom_detail_line = fields.One2many('fast.blank.bom.detail', 'bank_bom_id', string='相关BOM明细')
    company_id = fields.Many2one(related='bank_configuration_id.company_id', string='公司', store=True)

    name = fields.Char(related='bank_configuration_id.default_code', string='产品编码', store=True)

    product_tmpl_name = fields.Char('产品名称')
    code = fields.Char('参考')
    type = fields.Char('BOM类型')
    product_qty = fields.Char('数量')
    version = fields.Char('版本')

    product_name = fields.Char('产品变体')
    product_uom_nmae = fields.Char('计量单位')
    version_code = fields.Integer('版本号')
    create_user_char = fields.Char('创建人')
    create_date_char = fields.Char('创建时间')


class FastMrpBomDetail(models.Model):
    _name = 'fast.blank.bom.detail'
    _description = '自定义供应商bom明细只读'

    erp_id = fields.Integer('erp_id')
    bank_bom_id = fields.Many2one('fast.blank.bom', string='所属BOM', ondelete='cascade')
    product_name = fields.Char('物料')
    body = fields.Char('部位')
    need_qty = fields.Float('基础用量', digits=(16, 4))
    loss_qty = fields.Float('损耗率(%)', digits=(16, 4))
    product_qty = fields.Float('总用量', digits=(16, 4))
    product_uom_name = fields.Char(string='计量单位')
    bom_product_template_attribute_name = fields.Char('应用于变体')

    product_unit_price = fields.Float('计量单价', digits=(16, 4))
    purchase_unit_price = fields.Float('采购单价', digits=(16, 4))
    standard_price = fields.Float('金额', digits=(16, 4))


class FastProductCostPricingMaterial(models.Model):
    _name = "fast.product.cost.pricing.material"
    _description = '成本计价-物料成本'

    bank_configuration_id = fields.Many2one('fast.blank.configuration', '成本计价', ondelete='cascade')
    company_id = fields.Many2one(related='bank_configuration_id.company_id', string='公司', store=True)
    conf_type = fields.Selection([('main', '主料'), ('sub', '辅料'), ('blk', '空白版款式')], string='产品类型')

    product_id = fields.Char('物料')
    body = fields.Char('部位')
    need_qty = fields.Float('基础用量', digits=FLOAT_DIGITS)
    loss_qty = fields.Float('损耗率(%)', digits=FLOAT_DIGITS)
    product_qty = fields.Float('总用量', digits=FLOAT_DIGITS)
    sum_price = fields.Float('金额', digits=PRICE_DIGITS)
    spec = fields.Char('成分')
    f_width = fields.Float('边至边幅宽(cm)', digits=FLOAT_DIGITS)
    g_weight = fields.Float('克重', digits=FLOAT_DIGITS)
    purchase_price = fields.Float('采购价格', digits=PRICE_DIGITS,
                                  help='供应商报价中维护的报价：\n1、如果含税就取含税价；\n2、如果不含税就取不含税价')
    business_price = fields.Float('计量价格', digits=PRICE_DIGITS,
                                  help='供应商报价中维护的报价：\n1、如果含税就取含税价；\n2、如果不含税就取不含税价')
    uom_po_id = fields.Char('采购单位')
    assist_uom_id = fields.Char('计量单位')
    currency_id = fields.Many2one('res.currency', '货币', default=lambda self: self.env.company.currency_id.id)


class FastProductCostPricingSecondaryProcess(models.Model):
    _name = 'fast.product.cost.pricing.secondary.process'
    _description = '成本计价-二次工艺费用'

    bank_configuration_id = fields.Many2one('fast.blank.configuration', '成本计价', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='所属公司')
    currency_id = fields.Char('币种')
    name = fields.Char('名称')
    partner_id = fields.Char('加工厂')
    price = fields.Float(string='价格', digits=PRICE_DIGITS)
    remark = fields.Text('备注')


class FastProductCostPricingProcessingFee(models.Model):
    _name = "fast.product.cost.pricing.other.fee"
    _description = '成本计价-其它费用'

    bank_configuration_id = fields.Many2one('fast.blank.configuration', '成本计价', ondelete='cascade')
    company_id = fields.Many2one(related='bank_configuration_id.company_id', string='公司', store=True)
    currency_id = fields.Char('币种')
    name = fields.Char('费用项')
    price = fields.Float(string='价格', digits=PRICE_DIGITS)
    remark = fields.Text('备注')
