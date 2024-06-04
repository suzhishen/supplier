from odoo.http import content_disposition, dispatch_rpc, request, SessionExpiredException
from odoo.addons.fast_supplier_synergy.controllers.exception import OdooCustomHTTPException
from odoo import http
import datetime
import requests
import logging
import json
import odoo
import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import time
import base64
import re
import traceback
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Controller(http.Controller):
    @http.route('/api/packing_list_difference', type='http', auth='public', csrf=False, methods=['POST'])
    def packing_list_difference(self, **kwargs):
        record = request.env['fast.blank.packing_list_detail'].sudo()
        print(record)
        data = [{
            "id": "10001",
            "box_number": "箱号",
            "order_number": "订单号",
            "style_number": "款号",
            "color": "颜色",
            "xxs_4": "xxs_4",
        }, {
            "id": "10002",
            "box_number": "箱号1",
            "order_number": "订单号1",
            "style_number": "款号1",
            "color": "颜色1",
        }]
        return json.dumps({
            "code": 0,
            "msg": "请求成功",
            "count": 1,
            'data': data
        })

    @http.route('/api/test', type='http', auth='public', methods=['GET'])
    def test(self, **kwargs):
        data = [{"id":10000,"username":"user-0","sex":"女","city":"城市-0","sign":"签名-0","experience":255,"logins":24,"words":82830700,"classify":"作家","score":57},{"id":10001,"username":"user-1","sex":"男","city":"城市-1","sign":"签名-1","experience":884,"logins":58,"words":64928690,"classify":"词人","score":70.5},{"id":10002,"username":"user-2","sex":"女","city":"城市-2","sign":"签名-2","experience":650,"logins":77,"words":6298078,"classify":"酱油","score":31},{"id":10003,"username":"user-3","sex":"女","city":"城市-3","sign":"签名-3","experience":362,"logins":157,"words":37117017,"classify":"诗人","score":68},{"id":10004,"username":"user-4","sex":"男","city":"城市-4","sign":"签名-4","experience":807,"logins":51,"words":76263262,"classify":"作家","score":6},{"id":10005,"username":"user-5","sex":"女","city":"城市-5","sign":"签名-5","experience":173,"logins":68,"words":60344147,"classify":"作家","score":87},{"id":10006,"username":"user-6","sex":"女","city":"城市-6","sign":"签名-6","experience":982,"logins":37,"words":57768166,"classify":"作家","score":34},{"id":10007,"username":"user-7","sex":"男","city":"城市-7","sign":"签名-7","experience":727,"logins":150,"words":82030578,"classify":"作家","score":28},{"id":10008,"username":"user-8","sex":"男","city":"城市-8","sign":"签名-8","experience":951,"logins":133,"words":16503371,"classify":"词人","score":14},{"id":10009,"username":"user-9","sex":"女","city":"城市-9","sign":"签名-9","experience":484,"logins":25,"words":86801934,"classify":"词人","score":75}]
        return json.dumps({
            "code": 0,
            "msg": "请求成功",
            "count": 1,
            'data': data
        })

        # return request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
