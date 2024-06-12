from odoo import models,fields,api,_
from odoo.exceptions import UserError,ValidationError


class ZebrUpcTemplate(models.Model):
    _name = 'zebra.upc.template'
    _description = 'UPC模板'

    name = fields.Char('名称')
    code = fields.Char('编码')
    remark = fields.Char('备注')
    header_content = fields.Text('表头内容')
    content = fields.Text('标签内容')
    active = fields.Boolean(default=True)

    @api.constrains('code')
    def _check_code(self):
        count = self.search_count([('code', '=', self.code)])
        if count > 1:
            raise ValidationError('编码必须唯一！')