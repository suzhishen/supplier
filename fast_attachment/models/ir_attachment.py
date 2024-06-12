# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models, fields, api
import os
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    categ_id = fields.Many2one('ir.attachment.category', '文件类别')

    @api.model
    def search_panel_expands(self, field_name, **kwargs):
        return self.env['ir.attachment.category'].sudo().search([('is_expand', '=', True)]).mapped('id')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not args:
            root_categ_id = self.env.ref('fast_attachment.ir_attachment_category_all').id
            args.extend(['|', ('categ_id', 'child_of', root_categ_id), ('categ_id', 'parent_of', root_categ_id)])
        return super(IrAttachment, self)._search(args, offset=offset, limit=limit, order=order, count=False,
                                                 access_rights_uid=access_rights_uid)

    def action_download_file(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f"{base_url}/web/content/ir.attachment/{self.id}/datas?download=true"
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
        }

    def unlink(self):
        try:
            for order in self:
                # 当附件删除时，删除服务器filestore里面的文件
                if order.store_fname:
                    filepath = os.path.join(self._full_path(''), order.store_fname)
                    if os.path.exists(filepath):
                        os.remove(filepath)  # 删除源文件
            return super(IrAttachment, self).unlink()
        except Exception as e:
            raise UserError('发生错误，信息如下：\n%s' % str(e))

