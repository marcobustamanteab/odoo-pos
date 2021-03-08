# -*- coding: utf-8 -*-
from odoo import http
import json


class ConsultaStockMateriales(http.Controller):

    @http.route('/RESTAdapter/ConsultaStockMateriales360', methods=['POST'], auth='public', csrf=False, cors="*")
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
