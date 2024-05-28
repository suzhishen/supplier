from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
from odoo.tools import groupby
import concurrent.futures
import base64
import openpyxl
from io import BytesIO
import math

class FastBlankOrderMaterialRequirementsTask(models.Model):
    _name  = 'fast.blank.order.material.requirements.task'

    order_line = fields.Char()
    log_order_line = fields.Char( '订单中心--物料需求--任务--申领记录')
    qty_log_order_line = fields.Char('订单中心--物料需求--任务--补数记录')

    # 关联订单----裁床任务单
    cutting_task_id = fields.Char('裁床任务单')
    cutting_task_line_ids = fields.Char( string='裁床任务订单行')

    # 关联订单----委外订单
    outsource_order_blank_id = fields.Char(string='委外订单')
    outsource_order_blank_line_ids =fields.Char(string='委外订单行')

    # 来源信息
    origin_po = fields.Char('PO#', help='大PO#', readonly=1, store=1)
    origin = fields.Char('PO#', help='分配后的PO#', readonly=1, store=1)
    # order_qty = fields.Integer('订单数', readonly=1, store=1)
    origin_product_tmpl_id =fields.Char('款号-颜色', readonly=1, store=1)
    origin_product_ids = fields.Char( readonly=1, store=1)
    user_id = fields.Char(store=True)
    partner_id = fields.Char( store=True)
    order_type = fields.Char( readonly=1, store=1)

    # 物料信息
    product_id = fields.Char()
    product_configuration_id =fields.Char( store=True)
    product_default_code = fields.Char('编码',  store=True)
    product_default_name = fields.Char('名称', store=True)
    color_value_id = fields.Char( string='颜色', 
                                     store=True)
    color_cn_name = fields.Char(string='颜色', store=True)
    product_spec_id = fields.Char('规格', store=True)
    product_spec_remark = fields.Text('规格备注', store=True)
    conf_type = fields.Char(string='产品类型',store=True)
    assist_uom_id =fields.Char( store=True)
    uom_po_id = fields.Char( store=True)
    categ_id = fields.Char( store=True)
    f_width = fields.Char(store=True)
    g_weight =fields.Char(store=True)
    uom_conversio_char = fields.Char('单位转换系数', store=True,
                                    )
    uom_conversio_ratio = fields.Char('单位转换系数',store=True,
                                       )

    # 库存信息
    qty_available = fields.Float('总在库数',)
    can_use_inventory_qty = fields.Float('总自由库存', )
    po_occupancy_qty = fields.Float('PO占用库存', store=True)
    po_occupancy_can_use_qty = fields.Float('PO库存可用数', 
                                            store=True)
    this_po_occupancy_qty = fields.Float('本单占用库存', store=True)

    # 物料需求信息——数量
    product_qty = fields.Float('BOM需求数', store=True,
                               help='保留一位小数点，向上取整')
    reality_product_qty = fields.Float('实际需求数', help='确认需求时填写的数量')
    done_apply_qty = fields.Float('已申领数',readonly=1, store=1)
    pending_apply_qty = fields.Float('待申领数', 
                                     help='待申领数 = 申领需求数 - 已申领数')
    this_apply_qty = fields.Float('本次申领数',)

    remark = fields.Text('备注')

    # BOM信息
    body = fields.Char('部位',  store=True)

    state = fields.Char( string='物料状态',store=True,
                             help='不可用：总自由库存 + PO库存可用数 + 本单占用库存 = 0\n部分可用：总自由库存 + PO库存可用数 + 本单占用库存 < 待申领数\n全部可用：总自由库存 + PO库存可用数 + 本单占用库存 ≥ 待申领数')
    apply_state = fields.Char(store=True)
    is_close = fields.Boolean('已关闭', default=False, readonly=1, store=1)
