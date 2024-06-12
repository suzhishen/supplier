
import json
import operator
from odoo.http import content_disposition, request
from odoo.tools import  osutil

from odoo.addons.web.controllers.export import ExportFormat,GroupsTreeNode

def base(self, data):
    params = json.loads(data)
    model, fields, ids, domain, import_compat = \
        operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)
    Model = request.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
    if not Model._is_an_ordinary_table():
        fields = [field for field in fields if field['name'] != 'id']

    field_names = [f['name'] for f in fields]
    if import_compat:
        columns_headers = field_names
    else:
        columns_headers = [val['label'].strip() for val in fields]

    groupby = params.get('groupby')
    if not import_compat and groupby:
        groupby_type = [Model._fields[x.split(':')[0]].type for x in groupby]
        domain = [('id', 'in', ids)] if ids else domain
        groups_data = Model.read_group(domain, [x if x != '.id' else 'id' for x in field_names], groupby, lazy=False)

        # read_group(lazy=False) returns a dict only for final groups (with actual data),
        # not for intermediary groups. The full group tree must be re-constructed.
        tree = GroupsTreeNode(Model, field_names, groupby, groupby_type)
        for leaf in groups_data:
            tree.insert_leaf(leaf)

        response_data = self.from_group_data(fields, tree)
    else:
        records = Model.browse(ids) if ids else Model.search(domain, offset=0, limit=False, order=False)

        export_data = records.export_data(field_names).get('datas', [])
        response_data = self.from_data(columns_headers, export_data)

    # TODO: call `clean_filename` directly in `content_disposition`?
    filename = params.get('filename', '')
    file_name = (self.filename(model) + self.extension)
    if filename:
        file_name = f'{filename}-{file_name}'
    return request.make_response(response_data,
                                 headers=[('Content-Disposition',
                                           content_disposition(
                                               osutil.clean_filename(file_name))),
                                          ('Content-Type', self.content_type)],
                                 )

ExportFormat.base = base