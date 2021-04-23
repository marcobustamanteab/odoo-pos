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
            ('sync_account_move', 'Synchronize Accounting movement'),
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
        elif self.business_logic == 'sync_account_move':
            self._send_account_movement()

    # @api.onchange('request_id')
    # def _onchange_request_id(self):
    #     self.code = """task_response = self.env["integration.request"].browse(%s).action_perform_request()""" % (self.request_id.id)

    @api.model
    def run_task_from_cron(self, active_id):
        task = self.env['integration.task.definition'].browse(active_id).action_perform_task(guimode=False)

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

    def _get_stock_movement(self):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        if not settings.sync_stock_qty:
            _logger.debug("Stock Synchronization Disabled")
            return True
        return True

    def _send_account_movement(self):
        settings = self.env['integration.settings'].search([('company_id', '=', self.company_id.id)])
        movement = self.env['account.move'].search([('name', '=', 'INV/2021/04/0001')])
        journal_line = movement.line

        asiento_cabecera = {
            "T_DOCUMENTOS": {
                "CABECERA": {
                    "ID_DOCUMENTO": "%s" % movement.name,
                    "USERNAME": "KDCPEREZ",
                    "HEADER_TXT": "Asiento12221922",
                    "COMP_CODE": "A050",
                    "DOC_DATE": "%s" % movement.date.strftime("%Y%m%d"),
                    "PSTNG_DATE": "%s" % movement.date.strftime("%Y%m%d"),
                    "DOC_TYPE": "IA",
                    "REF_DOC_NO": "%s" % movement.payment_reference,
                    "TRANS_DATE": " "
                }}}

        # class_account = integration_accounting.class_account
        # type_account = integration_accounting.type_account
        # ind_ceco = integration_accounting.ind_ceco
        # ind_cebe = integration_accounting.ind_cebe

        for lines in journal_line:

            acreedor = {
              "ACREEDOR":[
                 {
                    "ITEMNO_ACC":"%s" % lines.company_id.id,
                    "VENDOR_NO":"%s" % lines.,
                    "SP_GL_IND":"",
                    "SGTXT":"",
                    "REF_KEY_1":"",
                    "REF_KEY_2":"",
                    "REF_KEY_3":"",
                    "BUS_AREA":"",
                    "BP_GEBER":"",
                    "PMNTTRMS":"",
                    "BLINE_DATE":"",
                    "PMNT_BLOCK":"",
                    "ALLOC_NMBR":"77019678-7",
                    "ALT_PAYEE":"",
                    "PROFIT_CTR":"A50B899200",
                    "PYMT_CUR":"",
                    "PYMT_AMT":""
                 }
              ]}
            creacion_vendor = {
                  "CREACION_VENDOR":[
                 {
                    "PAIS":"%s" % lines.company,
                    "RUT":"77019678-7",
                    "NOMBRE_1":"DISTRIBUIDORA L",
                    "NOMBRE_2":"DISTRIBUIDORA LA KAVA SPA",
                    "COD_BUSQUEDA":"77019678-7",
                    "DIRECCION":"Arauco 1025, Santiago 7700, 6",
                    "CALLE":"Arauco 1025, Santiago",
                    "NUMERO":"7700, 6",
                    "CIUDAD":"SANTIAGO",
                    "COMUNA":"LAS CONDES",
                    "REGION":"13",
                    "SOCIEDAD":"A050",
                    "CTA_ASOCIADA":"2102030011",
                    "GRUPO_TESORERIA":"KPN",
                    "VIA_PAGO":"V",
                    "CONDICION_PAGO":"Z000",
                    "ID_CUENTA_BANCARIA":"",
                    "PAIS_BANCO":"",
                    "CLAVE_BANCO":"",
                    "CUENTA_BANCARIA":""
                 }
              ]}
            deudor = {
              "DEUDOR":[
                 {
                    "ITEMNO_ACC":"0",
                    "CUSTOMER":" ",
                    "SP_GL_IND":" ",
                    "SGTXT":" ",
                    "PMNTTRMS":" ",
                    "PYMT_METH":" ",
                    "C_CTR_AREA":" ",
                    "TAX_CODE":" ",
                    "PROFIT_CTR":" ",
                    "BLINE_DATE":" ",
                    "PMNT_BLOCK":" ",
                    "REF_KEY_1":" ",
                    "REF_KEY_2":" ",
                    "REF_KEY_3":" ",
                    "ALT_PAYEE":" ",
                    "ALLOC_NMBR":" "
                 }
              ]}
            cuenta_de_mayor = {
                  "CUENTADEMAYOR":[
                 {
                    "ITEMNO_ACC":"2",
                    "HKONT":"2108010000",
                    "SGTXT":"",
                    "VALUE_DATE":" ",
                    "ALLOC_NMBR":"77019678-7",
                    "COSTCENTER":"",
                    "TAX_CODE":"",
                    "BUS_AREA":"",
                    "PLANT":"",
                    "MATERIAL":"",
                    "FUNC_AREA":"",
                    "FIS_PERIOD":"0",
                    "FISC_YEAR":"0",
                    "ALLOC_NMBR_2":"77019678-7",
                    "PROFIT_CTR":"A50B899200",
                    "WBS_ELEMENT":"",
                    "ORDERID":"",
                    "ASSET_NO":"",
                    "SALES_ORD":"",
                    "S_ORD_ITEM":"0",
                    "DISTR_CHAN":"",
                    "DIVISION":"",
                    "SALESORG":"",
                    "SALES_GRP":"",
                    "SALES_OFF":"",
                    "SOLD_TO":"",
                    "SEGMENT":"",
                    "REF_KEY_1":"",
                    "REF_KEY_2":"",
                    "REF_KEY_3":"",
                    "TRADE_ID":""
                 }
              ]}
            currency_amount = {
                  "CURRENCYAMOUNT":[
                 {
                    "ITEMNO_ACC":"1",
                    "CURR_TYPE":"0",
                    "CURRENCY":"CLP",
                    "CURRENCY_ISO":"0",
                    "AMT_DOCCUR":"-348750",
                    "AMT_BASE":"0",
                    "EXCH_RATE":".00000"
                 },
                 {
                    "ITEMNO_ACC":"2",
                    "CURR_TYPE":"0",
                    "CURRENCY":"CLP",
                    "CURRENCY_ISO":"0",
                    "AMT_DOCCUR":"348750",
                    "AMT_BASE":"0",
                    "EXCH_RATE":".00000"
                 }
              ]}
            criteria = {
              "CRITERIA":[
                 {
                    "ITEMNO_ACC":"0",
                    "FIELDNAME":" ",
                    "CHARACTER":" ",
                    "PROD_NO_LONG":" "
                 }
              ]}
        return True

        #print(asiento)
        # if not settings.sync_stock_qty:
        #     _logger.debug("Stock Synchronization Disabled")
        #     return True


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
