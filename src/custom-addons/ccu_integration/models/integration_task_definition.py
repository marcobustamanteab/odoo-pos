# -*- coding: utf-8 -*-
import json
import logging

import urllib3

_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IntegrationTaskDefinition(models.Model):
    _name = 'integration.task.definition'
    _description = 'Integration Task Definition'

    name = fields.Char()
    type = fields.Selection(
        [
            ('inmediate', 'Inmediate'),
            ('recurrent', 'Recurrente'),
        ]
        , string="Type")
    description = fields.Text("Description")
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit', default='months')
    active = fields.Boolean(default=True)
    code = fields.Text("Code")
    request_id = fields.Many2one("integration.request", string="Request")
    business_logic = fields.Selection(
        [
            ('sync_stock_1', 'Synchronize Stock from External Service 1'),
            ('sync_stock_2', 'Synchronize Stock from External Service 2'),
            ('send_stock_movement', 'Send Stock Movement'),
        ]
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.user.company_id.id)
    center_codes = fields.Char("Centers (a,b)")
    warehouse_codes = fields.Char("Warehouee (a,b)")
    param_line_ids = fields.One2many('integration.task.param', 'parent_id', string="Parameters")

    def action_perform_task(self, guimode=True):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        if not settings:
            msg = "Settings not found: Company %s" % (self.company_id.name)
            raise UserError(msg)
        if self.business_logic == 'sync_stock_1':
            settings, increase_products, decrease_products = self._sync_stock_1()
            if settings and (increase_products or decrease_products):
                picking_ids = self._sync_stock_gen_stock_pciking(settings, increase_products, decrease_products)
                if guimode:
                    return {
                        'name': _('Stock Picking Generated'),
                        'view_mode': 'tree',
                        'res_model': 'stock.picking',
                        'res_ids': picking_ids,
                        'view_id': self.env.ref('stock.vpicktree').id,
                        'type': 'ir.actions.act_window',
                        'domain': [('origin', '=', "INT_TASK_%s" % (self.id))],
                        'target': 'current'
                    }
        elif self.business_logic == 'sync_stock_2':
            settings, increase_products, decrease_products = self._sync_stock_2()
            if settings and (increase_products or decrease_products):
                picking_ids = self._sync_stock_gen_stock_pciking(settings, increase_products, decrease_products)
                if guimode:
                    return {
                        'name': _('Stock Picking Generated'),
                        'view_mode': 'tree',
                        'res_model': 'stock.picking',
                        'res_ids': picking_ids,
                        'view_id': self.env.ref('stock.vpicktree').id,
                        'type': 'ir.actions.act_window',
                        'domain': [('origin', '=', "INT_TASK_%s" % (self.id))],
                        'target': 'current'
                    }
        elif self.business_logic == 'send_stock_movement':
            self._send_stock_movement()

    # @api.onchange('request_id')
    # def _onchange_request_id(self):
    #     self.code = """task_response = self.env["integration.request"].browse(%s).action_perform_request()""" % (self.request_id.id)

    @api.model
    def run_task_from_cron(self, active_id):
        task = self.env['task.definition'].browse(active_id).action_perform_task(guimode=False)

    # BUSINESS LOGIC METHODS
    def _sync_stock_1(self):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        if not settings.sync_stock_qty:
            _logger.debug("Stock Synchronization Disabled")
            return True

        body = {}
        body["HEADER"] = {}
        body["HEADER"]["ID_MENSAJE"] = self._get_param("ID_MENSAJE")
        body["HEADER"]["MENSAJE"] = self._get_param("MENSAJE")
        body["HEADER"]["FECHA"] = self._get_param("FECHA")
        body["HEADER"]["SOCIEDAD"] = self._get_param("SOCIEDAD")
        body["HEADER"]["LEGADO"] = self._get_param("LEGADO")
        body["HEADER"]["CODIGO_INTERFAZ"] = self._get_param("CODIGO_INTERFAZ")
        body["CosulMat"] = []
        body["TabMate"] = []
        centers = self._get_param("Centro").split(",")
        warehouses = self._get_param("Almacen").split(",")
        for center in centers:
            for warehouse in warehouses:
                body["CosulMat"].append({'Centro': center, "Almacen": warehouse})
        # TODO: Sacar filtro de Articulos
        products = self.env['product.template'].search(
            [
                ('sync_stock_qty', '=', True),
                ('default_code', '!=', False),
                ('sale_ok', '=', 1),
                ('active', '=', 1),
                ('default_code', 'in', ['450235', '450344', 'ET11754']),
            ]
        )
        for prod in products:
            body["TabMate"].append({'Material': prod.default_code})

        payload = body

        request = self.env["integration.request"].browse(self.request_id.id)
        raw_response = request.action_perform_request(body=payload)
        if isinstance(raw_response, urllib3.HTTPResponse):
            if request.content_type == request.CT_JSON:
                response = json.loads(raw_response.data)
            else:
                raise UserError("Worng Request Response Object")
        response_root = response.get("ResponseConsultaStockMateriales_Inb", {})
        header = response_root.get("HEADER", {})
        detalleMat = response_root.get("CosulMat", [])
        increase_products = {}
        decrease_products = {}
        product_data = {}
        if isinstance(detalleMat, dict):
            detalleMat = [detalleMat]
        for detalle in detalleMat:
            centro = detalle.get("Centro")
            if not centro in product_data.keys():
                product_data[centro] = {}
            detalleMaterial = detalle.get("TabMate", [])
            if isinstance(detalleMaterial, dict):
                detalleMaterial = [detalleMaterial]
            for material in detalleMaterial:
                if material.get("Mensaje", "Error") != "OK":
                    continue
                if not material.get("Material", ""):
                    continue
                product = self.env['product.template'].search([('default_code', '=', material.get("Material"))], limit=1)
                if not product:
                    continue
                product_code = material.get("Material")
                current_stock = float(material.get("Stock", "0.0"))
                product_stock = product.qty_available
                stock_diff = current_stock - product_stock
                if not centro in increase_products.keys():
                    increase_products[centro] = {}
                if not centro in decrease_products.keys():
                    decrease_products[centro] = {}
                if stock_diff > 0:
                    increase_products[centro][product_code] = stock_diff
                elif stock_diff < 0:
                    decrease_products[centro][product_code] = abs(stock_diff)
        return settings, increase_products, decrease_products

    def _sync_stock_gen_stock_pciking(self, settings, increase_products, decrease_products):
        picking = self.env["stock.picking"]
        picking_ids = []
        stages = ['increase', 'decrease']
        picking_types = [settings.increase_picking_type_id, settings.decrease_picking_type_id]
        stock_info = [increase_products, decrease_products]
        des_loc_field = ['location_dest_id', 'location_id']
        for stage in range(0, 2):
            # print(stages[stage])
            # XCREASE
            for centro in stock_info[stage].keys():
                if stock_info[stage][centro].keys():
                    vals = {}
                    vals["picking_type_id"] = picking_types[stage].id
                    vals["location_id"] = picking_types[stage].default_location_src_id.id
                    vals["location_dest_id"] = picking_types[stage].default_location_dest_id.id
                    vals["origin"] = "INT_TASK_%s" % (self.id)

                    dest_location = self.env['stock.location'].search([('name', '=', centro)])
                    if dest_location:
                        vals[des_loc_field[stage]] = dest_location[0].id
                    items = []
                    for product_code in stock_info[stage][centro]:
                        product = self.env['product.template'].search([('default_code', '=', product_code)],limit=1)
                        items.append(
                            (0, 0,
                             {'product_id': product.id,
                              'name': product.name,
                              'product_uom': product.uom_id.id,
                              'product_uom_qty': stock_info[stage][centro][product_code]})
                        )
                    vals['move_lines'] = items
                    new_picking = picking.create(vals)
                    picking_ids.append(new_picking.id)
        return picking_ids

    def _sync_stock_2(self):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        if not settings.sync_stock_qty:
            _logger.debug("Stock Synchronization Disabled")
            return True
        url = "http://wso2qa5.ccu.cl:8280/services/SelectStockOnlineDSS/api/IMA14"

        payload = ""
        urivalues = [param.value for param in self.param_line_ids if param.scope == IntegrationTaskDefinitionParam.S_URL]
        par_keys = [param.key for param in self.param_line_ids if param.scope == IntegrationTaskDefinitionParam.S_HEADER]
        par_values = [param.value for param in self.param_line_ids if param.scope == IntegrationTaskDefinitionParam.S_HEADER]
        header = dict(zip(par_keys, par_values))
        request = self.env["integration.request"].browse(self.request_id.id)
        raw_response = request.action_perform_request(body=payload,
                                                      urivalues=urivalues,
                                                      header=header)
        if isinstance(raw_response, urllib3.HTTPResponse):
            if request.content_type == request.CT_JSON:
                print(["RESPONSE_DATA_TYPE", type(raw_response.data)])
                print(["RESPONSE_DATA", raw_response.data])
                response = json.loads(raw_response.data)
            else:
                print(["RESPONSE_DATA_TYPE", type(raw_response.data)])
                print(["RESPONSE_DATA", raw_response.data])
                response = raw_response.data
            try:
                response = json.loads(raw_response.data)
            except json.JSONDecoder as errstring:
                response = raw_response.data
            # print(["TYPE", type(response)])
            # print(["TYPE", dir(response)])
            # return None, None, None

            root_items = response.get("items", {})
            item_list = root_items.get("item", [])
            increase_products = {}
            decrease_products = {}

            for item in item_list:
                product_code = item.get("INV_ITEM_ID")
                product = self.env['product.template'].search(
                    [
                        ('sync_stock_qty', '=', True),
                        ('default_code', '!=', False),
                        ('sale_ok', '=', 1),
                        ('active', '=', 1),
                        ('default_code', '=', product_code),
                    ]
                )
                if not product:
                    continue
                current_stock = float(item.get("QTY", 0.0))
                product_stock  = product.qty_available
                stock_diff = current_stock - product_stock
                centro = item.get("BUSINESS_UNIT","")
                if not centro in increase_products.keys():
                    increase_products[centro] = {}
                if not centro in decrease_products.keys():
                    decrease_products[centro] = {}
                if stock_diff > 0:
                    increase_products[centro][product_code] = stock_diff
                elif stock_diff < 0:
                    decrease_products[centro][product_code] = abs(stock_diff)

        else:
            raise UserError("Worng Request Response Object")

        return settings, increase_products, decrease_products

    def _send_stock_movement(self):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        if not settings.sync_stock_qty:
            _logger.debug("Stock Synchronization Disabled")
            return True
        return True



    def _get_param(self, key):
        res = ""
        for param in self.param_line_ids:
            if param.key == key:
                if param.value_type == 'fixed':
                    res = param.value
                else:
                    res = param.value
                break
        return res


class IntegrationTaskDefinitionParam(models.Model):
    _name = "integration.task.param"
    _description = "Integration Task Definition Param"

    S_HEADER = 'header'
    S_URL = 'url'
    S_FIELD = 'field'
    S_QUERY = 'query'

    def _get_default_parent_id(self):
        return self._context.get("parent_id")

    parent_id = fields.Many2one('integration.task.definition',
                                string="Task Definition",
                                required=True,
                                default=_get_default_parent_id)
    # parent_id = fields.Integer("ParentID")
    key = fields.Char(string="Key")
    value_type = fields.Selection(
        [
            ('fixed', 'Fixed Value'),
            ('python', 'Python Expression'),
            ('orm', 'ORM Expression'),
        ], string="Value Type", default="fixed")
    value = fields.Char("Value")
    scope = fields.Selection(
        [
            (S_HEADER, 'Header'),
            (S_URL, 'Add to URL'),
            (S_FIELD, 'Field'),
            (S_QUERY, 'Query'),
        ]
    )
