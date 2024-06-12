from odoo import models, fields, api, _


class FastSupplierOrderBlankWizard(models.TransientModel):
    _name = 'fast.supplier.order.blank.wizard'
    _inherit = 'fast.supplier.order.blank'
    _description = '订单中心--物料需求--向导'

    main_material_order_wizard_line = fields.One2many('fast.blank.order.material.requirements.wizard', 'outsource_order_blank_wizard_id',
                                                      string='相关物料需求(主料)--向导', domain=[('conf_type', '=', 'main')])

    def _get_action(self):
        action = self.env.ref('fast_supplier_synergy.fast_supplier_order_blank_wizard_action').sudo().read()[0]
        action['res_id'] = self.id
        action['target'] = 'new'
        action['context'] = {'dialog_size': 'extra-modal-max-90'}
        return action


class FastBlankOrderMaterialRequirementsWizard(models.TransientModel):
    _name = 'fast.blank.order.material.requirements.wizard'
    _inherit = 'fast.blank.order.material.requirements'
    _description = '订单中心--物料需求--向导'
    _order = 'outsource_order_blank_id'

    # 关联主表
    outsource_order_blank_wizard_id = fields.Many2one('fast.supplier.order.blank.wizard', string='所属空白版委外加工单--向导', ondelete='cascade')


