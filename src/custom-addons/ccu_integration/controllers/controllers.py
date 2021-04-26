# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.http import content_disposition, Controller, request, route, Response
import json
import logging
from html import unescape

_logger = logging.getLogger(__name__)


class ConsultaStockMateriales(Controller):

    @route('/check_connection', methods=['GET',], auth='public', csrf=False, cors="*")
    def check_connection(self):
        res_data = {"Connection":"OK", "TimeStamp":str(datetime.now())}
        return json.dumps(res_data)

    @route('/restapi/private/stock_movement/confirmation', methods=['POST',], type='json', auth='public', csrf=False, cors="*")
    def stock_movement_confirmation(self):
        res_data = {"Connection":"OK", "TimeStamp":str(datetime.now())}
        req = request.httprequest
        res_data["headers"] = {}
        for head in req.headers.keys():
            res_data["headers"][head] = req.headers.get(head)
        payload = json.loads(req.data.decode('utf-8'))
        _logger.info("DICT TYPE %s", type(payload))
        new_log = request.env['integration.request.log'].sudo()
        request_id = request.env['integration.request'].sudo().search(
            [
                ('ref','=',req.headers.get('CODIGO_INTERFAZ','NONE')),
            ], limit=1)
        log = new_log.create_log(request_id=request_id.id if request else None,
                                 header=req.headers,
                                 payload=payload,
                                 traffic='inbound')
        return json.dumps(res_data)

    @route('/stock_consult', methods=["POST"], auth='public', csrf=False, cors="*")
    def consulta_stock_materiales(self, **kw):
        res_data = {
                "ResponseConsultaStockMateriales_Inb": {
                    "HEADER": {
                        "ID_MENSAJE": "0 ",
                        "MENSAJE": "OK",
                        "FECHA": "20210212",
                        "SOCIEDAD": "OK",
                        "LEGADO": "BUS",
                        "CODIGO_INTERFAZ": "ITD_009"
                    },
                    "CosulMat": [
                        {
                            "Centro": "2301",
                            "Almacen": "PT01",
                            "TabMate": [
                                {
                                    "Material": "450229",
                                    "Stock": "1784.000 ",
                                    "Codigo": "0 ",
                                    "Mensaje": "OK"
                                },
                                {
                                    "Material": "450230",
                                    "Stock": "314.000 ",
                                    "Codigo": "0 ",
                                    "Mensaje": "OK"
                                }
                            ]
                        },
                        {
                            "Centro": "9001",
                            "Almacen": "PT01",
                            "TabMate": {
                                "Material": "ET11754",
                                "Stock": "91.000 ",
                                "Codigo": "0 ",
                                "Mensaje": "OK"
                            }
                        }
                    ]
                }
            }
        return json.dumps(res_data)

    @route('/restapi/private/account_move/return', methods=['POST'], type='json', auth='public', csrf=False, cors="*")
    def stock_movement_confirmation(self):
        res_data = {"Connection":"OK", "TimeStamp":str(datetime.now())}
        req = request.httprequest
        res_data["headers"] = {}
        for head in req.headers.keys():
            res_data["headers"][head] = req.headers.get(head)
        payload = json.loads(req.data.decode('utf-8'))
        _logger.info("DICT TYPE %s", type(payload))
        new_log = request.env['integration.request.log'].sudo()
        request_id = request.env['integration.request'].sudo().search(
            [
                ('ref','=',req.headers.get('CODIGO_INTERFAZ','NONE')),
            ], limit=1)
        log = new_log.create_log(request_id=request_id.id if request else None,
                                 header=req.headers,
                                 payload=payload,
                                 traffic='inbound')
        return json.dumps(res_data)

# ejemplo respuesta sap
# {
#     "SOCIEDAD": "A031",
#     "LEGADO": "TRUCK",
#     "ID_MENSAJE": "2c7f616d-d99e-3aea-90c0-acc89df336b0",
#     "FECHA": 20210424,
#     "MENSAJE": "Registro asiento contable",
#     "CODIGO_INTERFAZ": "RTR_038",
#     "respuesta": [
#         {
#             "id_documento": "SE210228162703000O",
#             "id_referencia": {
#                 "codigo": "P-001",
#                 "mensaje": "Documento ya se encuentra creado en la BD. Documento: 3200010401"
#             }
#         }
#     ]
# }

