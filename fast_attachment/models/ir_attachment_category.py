# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError


class IrAttachmentCategory(models.Model):
    _name = 'ir.attachment.category'
    _description = '文件类别'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'id asc, name asc'

    name = fields.Char('名称', index='trigram', required=True)
    complete_name = fields.Char('完整名称', compute='_compute_complete_name', recursive=True, store=True)
    parent_id = fields.Many2one('ir.attachment.category', '上级分类', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many('ir.attachment.category', 'parent_id', '子级分类')

    is_expand = fields.Boolean('是否展开', default=True)
    active = fields.Boolean('有效', default=True)

    @api.model
    def search_panel_expands(self, field_name, **kwargs):
        return self.sudo().search([('is_expand', '=', True)]).mapped('id')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('您不能创建递归类别。'))

    @api.model
    def name_create(self, name):
        return self.sudo().create({'name': name}).name_get()[0]

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super().name_get()

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_category(self):
        main_category = self.env.ref('fast_attachment.ir_attachment_category_all', raise_if_not_found=False)
        if main_category and main_category in self:
            raise UserError(_("您不能删除此类别【%s】，它是默认的常规类别。" % main_category.name))
        process_category = self.env.ref('fast_attachment.ir_attachment_category_process_sheet',
                                        raise_if_not_found=False)
        if process_category and process_category in self:
            raise UserError(_("您不能删除此类别【%s】，它是默认的常规类别。" % process_category.name))
        diagram_category = self.env.ref('fast_attachment.ir_attachment_category_frame_diagram',
                                        raise_if_not_found=False)
        if diagram_category and diagram_category in self:
            raise UserError(_("您不能删除此类别【%s】，它是默认的常规类别。" % diagram_category.name))
        size_category = self.env.ref('fast_attachment.ir_attachment_category_size_table', raise_if_not_found=False)
        if size_category and size_category in self:
            raise UserError(_("您不能删除此类别【%s】，它是默认的常规类别。" % size_category.name))
        other_category = self.env.ref('fast_attachment.ir_attachment_category_other', raise_if_not_found=False)
        if other_category and other_category in self:
            raise UserError(_("您不能删除此类别【%s】，它是默认的常规类别。" % other_category.name))
