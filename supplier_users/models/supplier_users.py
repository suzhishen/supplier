from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
from passlib.context import CryptContext


class SupplierUsers(models.Model):
    _inherit = 'res.users'

    subordinate_ids = fields.One2many('res.users', 'superiors_id', string='相关下属')
    superiors_id = fields.Many2one('res.users', string='所属上级', compute='_compute_superiors_id', store=True)

    @api.depends('login')
    def _compute_superiors_id(self):
        self.superiors_id = self.create_uid.id

    def change_password_wizard_view_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': '修改密码',
            'target': 'new',
            'view_mode': 'form',
            'res_model': 'supplier.change.password.wizard'
        }


class SupplierChangePasswordWizard(models.TransientModel):
    """ A wizard to manage the change of users' passwords. """
    _name = "supplier.change.password.wizard"
    _description = "Supplier Change Password Wizard"

    def _default_user_id(self):
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        return user_ids[0]

    user_login = fields.Many2one('res.users', string='User Login', readonly=True, default=_default_user_id)
    login = fields.Char(related='user_login.login', string='账号', readonly=True)
    new_passwd = fields.Char(string='新密码', default='')

    def supplier_change_password_button(self):
        self.ensure_one()
        password = CryptContext(schemes=['pbkdf2_sha512']).hash(self.new_passwd)
        sql = "UPDATE res_users SET password = '%s' WHERE ID = %s" % (password, self.user_login.id)
        self.env.cr.execute(sql)

