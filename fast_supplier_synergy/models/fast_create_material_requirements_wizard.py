import math
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import concurrent.futures
from odoo.tools import groupby
import requests
DIGITS = "Product Unit of Measure"


class FastCreateMaterialRequirementsWizard(models.TransientModel):
    _name = 'fast.create.material.requirements.wizard'
    _description = '录入订单--确认物料需求'

    # 关联订单----空白版订单
    blank_order_id = fields.Char('空白版订单')
    blank_order_line_ids = fields.Char( string='空白版订单行')

    # 关联订单----裁床任务单
    cutting_task_id = fields.Char('裁床任务单')
    cutting_task_line_ids = fields.Char( string='裁床任务订单行')

    # 关联订单----委外订单
    outsource_order_blank_id = fields.Char( string='委外订单')
    outsource_order_blank_line_ids = fields.Char(string='委外订单行')

    product_tmpl_id = fields.Char('款式')
    default_code = fields.Char('款式')
    order_qty = fields.Integer('订单数')

    order_line = fields.One2many('fast.create.material.requirements.wizard.line', 'order_id', '需求明细')
    main_order_line = fields.One2many('fast.create.material.requirements.wizard.line', 'order_id', '主料需求明细', domain=[('conf_type', '=', 'main')])
    sub_order_line = fields.One2many('fast.create.material.requirements.wizard.line', 'order_id', '辅料需求明细', domain=[('conf_type', '=', 'sub')])

    select_all_main = fields.Boolean('选择', default=False)
    select_all_sub = fields.Boolean('选择', default=False)
    erp_id = fields.Json(string='存放ERP记录ID')
    def btn_save_by_apply_material(self):
        order_line = self.order_line.filtered(lambda x: x.select)
        if not self.order_line:
            raise UserError('操作无法完成：不存在物料需求明细！')
        elif not order_line:
            raise UserError('操作无法完成：请选择需要申领的物料！')
        values = []
        
        for product_tmpl_name in order_line:
                self.env['fast.blank_order_detail'].search([('product_color_name','in',product_tmpl_name.erp_id['product_tmpl_default_code'])]).is_material_requirements_confirmed = True
        for product_id,product_value in groupby(order_line,lambda x:x.product_id):
            outsource_order_blank_line_ids = []
            origin_product_ids = []
            erp_product = None
            reality_product_qty = 0
            order_line_data = []
            for line in product_value:
                order_line_data.append({
                            "order_qty": line.order_qty,
                            "os_assist_product_qty": line.os_assist_product_qty,
                            "assist_product_qty":line.assist_product_qty,
                            "bom_need_qty":line.bom_need_qty,
                            "bom_loss_qty":line.bom_loss_qty,
                            "bom_product_qty": line.bom_product_qty,
                            "body": line.body,
                        })
                reality_product_qty += line.reality_product_qty
                erp_product = line.erp_id['product_id']
                outsource_order_blank_line_ids+=line.erp_id['outsource_order_blank_line_ids']
                origin_product_ids += line.erp_id['origin_product_ids']
            values.append({
                "outsource_order_blank_id": self.erp_id['outsource_order_blank_id'],
                "outsource_order_blank_line_ids": list(set(outsource_order_blank_line_ids)),
                "order_type":  self.erp_id['order_type'],
                "origin_po":  self.erp_id['origin_po'],
                "origin":  self.erp_id['origin'],
                "origin_product_tmpl_id": self.erp_id['origin_product_tmpl_id'],
                "origin_product_ids": self.erp_id['origin_product_ids'],
                "product_id": erp_product,
                "reality_product_qty": reality_product_qty,
                "order_line":order_line_data,
              }) 
                #    'reality_product_qty': 0,
                # 'remark': 'order_type',
        headers = {'Content-Type': 'application/json'}
        Dev_url = self.env['fast.config.dev'].sudo().get_dev_url()
        response = requests.post(url=f'{Dev_url}/supplier_sync_data_create_fast_blank_order_material_requirements_task', json={'params':{'datas':values}}, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['result']['type'] == 'ok':
                material_requirements = []
                outsource_order_blank_id = self.env['fast.supplier.order.blank'].search([('name','=',self.erp_id['origin'])])
                for line in self.order_line:
                    if line.select == True:
                        material_requirements.append({
                            'outsource_order_blank_id':outsource_order_blank_id.id,
                            'product_default_code':line.product_default_code,
                            'product_default_name':line.product_default_name,
                            'color_value_name':line.color_attr_id,
                            'color_cn_name':line.color_cn_name,
                            'conf_type':line.conf_type,
                            'product_qty':line.apply_product_qty,
                            'apply_qty':line.reality_product_qty,
                            "uom_po_name":line.uom_po_id,
                            "price":line.bom_price,
                            "uom_po_name":line.uom_po_id,
                            'ship_qty':0,
                            'body':line.body,
                            'categ_name':'categ_name',
                        })
                self.env['fast.blank.order.material.requirements'].create(material_requirements)
            



    @api.onchange('select_all_main')
    def onchange_select_all_main(self):
        self.main_order_line.filtered(lambda x: not x.is_apply).update({'select': self.select_all_main})

    @api.onchange('select_all_sub')
    def onchange_select_all_sub(self):
        self.sub_order_line.filtered(lambda x: not x.is_apply).update({'select': self.select_all_sub})


class FastCreateMaterialRequirementsWizardLine(models.TransientModel):
    _name = 'fast.create.material.requirements.wizard.line'
    _description = '录入订单--确认物料需求--详情'
    _order = 'product_id, bom_product_qty desc'

    order_id = fields.Many2one('fast.create.material.requirements.wizard', '关联主表', ondelete='cascade')

    # 订单信息
    order_qty = fields.Integer('订单数', readonly=1, store=True)
    origin_product_ids = fields.Char()

    # 物料信息
    product_id = fields.Char('物料')
    product_default_code = fields.Char('物料编码',)
    product_default_name = fields.Char('物料名称')
    conf_type = fields.Char( string='产品类型')
    uom_po_id = fields.Char( '采购单位')
    assist_uom_id = fields.Char('uom.uom')
    product_color_id = fields.Char(store=True)
    product_spec_id = fields.Char('物料规格')
    product_spec_remark = fields.Text('规格备注',)
    color_attr_id = fields.Char(string='物料颜色',)
    # color_cn_name = fields.Char('颜色', compute='_compute_color_cn_name', store=True, help='颜色中文名称')
    color_cn_name = fields.Char('颜色', store=True, help='颜色中文名称')
    product_uom_conversio_char = fields.Char('单位转换系数', )
    product_uom_conversio_ratio = fields.Float('单位转换系数',  )

    # BOM信息
    body = fields.Char('部位', readonly=1,)
    bom_need_qty = fields.Float('单件均码净用量', )
    bom_loss_qty = fields.Float('单件均码损耗率(%)')
    bom_product_qty = fields.Float('单件均码总用量')

    # 需求信息
    os_assist_product_qty = fields.Float('均码业务需求数', digits=DIGITS, readonly=1, store=True)
    assist_product_qty = fields.Float('细码业务需求数', digits=DIGITS, readonly=1, store=True)
    product_qty = fields.Float('采购需求数', digits=DIGITS, compute='_compute_product_qty', store=True)
    apply_product_qty = fields.Float('BOM需求数', digits=DIGITS, compute='_compute_apply_product_qty', store=True)
    reality_product_qty = fields.Float('物料申领数', digits=DIGITS, help='确认需求时填写的数量')
    quantity_issued = fields.Float(string='已发料数')
    quantity_unissued = fields.Float(string='未发料数')    
    # 默认供应商信息
    supplier_quotation_line_id = fields.Char( '供应商报价明细行ID')
    uom_conversio_char = fields.Char('单位转换系数'
                                     )
    uom_conversio_ratio = fields.Float('单位转换系数', 
                                      )
    partner_id = fields.Char( '默认供应商')
    partner_product_code = fields.Char('物料编码')
    partner_product_name = fields.Char('物料名称')
    f_width = fields.Float('边至边幅宽(cm)')
    g_weight = fields.Float('克重')
    is_apply = fields.Boolean('已确认')
    # 其它信息
    select = fields.Boolean('选择', default=False)
    remark = fields.Text('备注')
    bom_price = fields.Float(string='BOM价格')
    erp_id = fields.Json(string='存放ERP记录ID')
