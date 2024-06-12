from odoo import models,fields,api,_
from odoo.addons.web.models.models import Base


"""返回默认展开的类别，可重写继承"""
@api.model
def search_panel_expands(self, field_name, **kwargs):
    field = self._fields[field_name]
    Comodel = self.env[field.comodel_name].with_context(hierarchical_naming=False)
    # field_names = ['display_name']
    # comodel_records = Comodel.search_read([])
    # return [1, 7]
    return []

Base.search_panel_expands = search_panel_expands