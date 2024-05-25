# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrAttachmentExtend(models.Model):
    _inherit = 'ir.attachment'

    file_size_mb = fields.Char(string='文件大小 (KB)', compute='_compute_file_size_mb')

    @api.depends('file_size')
    def _compute_file_size_mb(self):
        for attachment in self:
            kb = attachment.file_size / 1024
            mb = round(kb, 0)
            attachment.file_size_mb = str(int(mb)) + 'KB'


