#encoding: utf-8
from odoo import fields, models, api

class IntegrationSettings(models.Model):
    _name = "integration.settings"
    _description = "Settings for Integration"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    name = fields.Char("Name", related="company_id.name", store=True)
    increase_picking_type_id = fields.Many2one('stock.picking.type', string="Increase Picking Type", domain=[('code','=','incoming')])
    decrease_picking_type_id = fields.Many2one('stock.picking.type', string="Decrease Picking Type", domain=[('code','=','outgoing')])
    sync_stock_qty = fields.Boolean("Synchroniza Stock Qty.")

    #     def sss(self):
    # body = {}
    # body["HEADER"] = {}
    # body["HEADER"]["ID_MENSAJE"] = "0"
    # body["HEADER"]["MENSAJE"] = "OK"
    # body["HEADER"]["FECHA"] = "20191118"
    # body["HEADER"]["SOCIEDAD"] = "B011"
    # body["HEADER"]["LEGADO"] = "BUS"
    # body["HEADER"]["CODIGO_INTERFAZ"] = "ITD_009"
    # body["HEADER"]["CosumlMat"] = []
    # body["HEADER"]["TabMate"] = []
    # products = self.env['product.template'].search(
    #     [
    #         ('sync_stock_qty','=',True)
    #     ]
    # )
    # centers = ['2301','9001']
    # locations = ['PT01']
    # for center in centers:
    #     for location in locations:
    #         body["HEADER"]["CosumlMat"].append({'Centro':center,"Almacen":location})
    # for prod in products:
    #     body["HEADER"]["TabMate"].append({'Material': prod.default_code})
    # self.env["product.product"].search("")
    # {
    #     "HEADER": {
    #         "ID_MENSAJE": "0",
    #         "MENSAJE": "OK",
    #         "FECHA": "20191118",
    #         "SOCIEDAD": "B011",
    #         "LEGADO": "BUS",
    #         "CODIGO_INTERFAZ": "ITD_009"
    #     },
    #     "CosulMat": [
    #         {
    #             "Centro": "2301",
    #             "Almacen": "PT01"
    #         },
    #         {
    #             "Centro": "9001",
    #             "Almacen": "PT01"
    #         }
    #     ],
    #     "TabMate": [
    #         {
    #             "Material": "450229"
    #         },
    #         {
    #             "Material": "450230"
    #         },
    #         {
    #             "Material": "ET11754"
    #         }
    #     ]
    # }