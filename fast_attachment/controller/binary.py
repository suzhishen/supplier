from odoo.addons.web.controllers.binary import Binary, clean
import base64, json, logging, unicodedata

from odoo import http, _
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class CusBinary(Binary):

    @http.route('/web/binary/upload_attachment', type='http', auth="user")
    # def upload_attachment(self, model, id, categ_id, upload_file_to_oos, ufile, callback=None):
    def upload_attachment(self, model, id, ufile, callback=None, categ_id=False):
        files = request.httprequest.files.getlist('ufile')
        Model = request.env['ir.attachment']
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        args = []
        for ufile in files:
            filename = ufile.filename
            if request.httprequest.user_agent.browser == 'safari':
                # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                # we need to send it the same stuff, otherwise it'll fail
                filename = unicodedata.normalize('NFD', ufile.filename)
            try:
                val = {
                    'name': filename,
                    'datas': base64.encodebytes(ufile.read()),
                    'res_model': model,
                    'res_id': int(id)
                }
                if categ_id and categ_id != 'false':
                    val['categ_id'] = int(categ_id)
                else:
                    val['categ_id'] = request.env.ref('fast_attachment.ir_attachment_category_all').id
                attachment = Model.create(val)
                attachment._post_add_create()
            except AccessError:
                args.append({'error': _("You are not allowed to upload an attachment here.")})
            except Exception:
                args.append({'error': _("Something horrible happened")})
                _logger.exception("Fail to upload attachment %s", ufile.filename)
            else:
                args.append({
                    'filename': clean(filename),
                    'mimetype': ufile.content_type,
                    'id': attachment.id,
                    'size': attachment.file_size
                })
        return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)
