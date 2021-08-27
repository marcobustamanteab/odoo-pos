# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# Copyright (C) 2021 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime

from odoo import api, fields, models
import logging, time
from odoo.exceptions import ValidationError
import uuid
import logging
import json

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Campos para recibir confirmación de sincronización
    sync_uuid = fields.Char(string='Sync. UUID', readonly=True, index=True, tracking=True,
                            default=lambda self: str(uuid.uuid4()))
    is_sync = fields.Boolean(string='Synchronize', default=False, tracking=True)
    sync_text = fields.Text(string='Sync. Text', readonly=True, tracking=True)
    posted_payload = fields.Text('Posted Payload', readonly=True)
    response_payload = fields.Text('Response Payload', readonly=True)

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for rec in self:
            if not rec.sync_uuid:
                rec.write({'sync_uuid': str(uuid.uuid4())})
            rec.esb_send_stock_out()
        return res

    def esb_send_stock_out(self):
        self.ensure_one()
        payload_lines = []
        esb_api_endpoint = "/sap/inventario/movimiento/crear"
        backend = self.company_id.backend_esb_id
        if not self.sync_uuid:
            self.write({'sync_uuid': str(uuid.uuid4())})

        centro = self.location_id.location_id.ccu_code or self.location_dest_id.location_id.ccu_code
        cost_center_code = self.location_id.location_id.cost_center_code or self.location_dest_id.location_id.cost_center_code

        almacen = self.location_id.ccu_code or self.location_dest_id.ccu_code

        # Solo si el almacen de entrada y salida poseen código CCU
        if not almacen:
            msg = 'Location without ccu code: ' + self.location_id.name
            raise ValidationError(msg)
        else:
            # Document Data from pos_order
            # year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
            fecha_AAAAMMDD = datetime.datetime.now().strftime("%Y%m%d")
            id_documento = self.pos_order_id.account_move.name or ''

            if self.pos_order_id.account_move.date:
                # year, month, day, hour, min = map(int, self.pos_order_id.account_move.date.strftime(
                #     "%Y %m %d %H %M").split())
                doc_date = self.pos_order_id.account_move.date.strftime("%Y%m%d")
            else:
                doc_date = ''

            payload = {
                "HEADER": {
                    "ID_MENSAJE": self.sync_uuid,
                    "MENSAJE": "Inventory Movements from Odoo",
                    "FECHA": fecha_AAAAMMDD,
                    "SOCIEDAD": self.company_id.ccu_business_unit,
                    "LEGADO": "ODOO-POS",
                    "CODIGO_INTERFAZ": "ITD058_ODOO"
                },
                "t_movimiento": {
                    "cabecera": {
                        "id_documento": self.name,
                        "username": backend.user,
                        "header_txt": self.origin,
                        "doc_date": doc_date,
                        "pstng_date": fecha_AAAAMMDD,  # es fecha contable
                        "ref_doc_no": self.origin,
                    },
                    "detalle": payload_lines
                }
            }
            # code_deptm = warehouse_id.analytic_account_id.code or self.company_id.esb_default_analytic_id.code

            i = 0
            for line in self.move_line_ids:
                i = i + 1
                if line.product_id.default_code and line.product_id.type == 'product':
                    payload_lines.append({
                        "pos_num": str(i),
                        "hkont": {},
                        "costcenter": cost_center_code or "",
                        "text": {},
                        "plant": centro,
                        "material": line.product_id.default_code,
                        "stge_loc": almacen,  # Almacen SAP/ubicación Odoo
                        "move_stloc": "0",
                        "batch": "NONE",
                        "entry_qnt": line.qty_done,
                        "item_text": line.picking_id.origin,
                        "move_type": line.move_id.picking_type_id.ccu_code_usage
                    })

            if len(payload_lines) >= 1:
                json_object = json.dumps(payload, indent=4)
                print(json_object)

                self.write({
                    'posted_payload': json_object}
                )
                res = backend.api_esb_call("POST", esb_api_endpoint, payload)

                dcto_sap = int(res['mt_response']['HEADER']['reference'])
                if dcto_sap > 0:
                    self.write({
                        'is_sync': True,
                        'sync_text': str(dcto_sap),
                        'response_payload': json.dumps(res, indent=4)}
                    )
                else:
                    json_object = json.dumps(payload, indent=4)
                    json_object_response = json.dumps(res, indent=4)
                    msg = "SAP response with error\n input data:\n" + json_object + "\nOUTPUT:\n" + json_object_response
                    raise ValidationError(msg)

    @api.model
    def send_picking_to_ESB(self):
        if self.picking_type_id.ccu_sync:
            self.with_delay(channel='root.inventory').esb_send_stock_out()

    def action_send_picking_to_ESB(self):
        self.send_picking_to_ESB()

    def update_sync(self, status='NO OK', message='none'):
        # picking = self.env['stock.picking'].browse(picking_put_request.stock_picking_id)
        if 'NO OK' in status:
            self.sudo().write({
                'is_sync': False,
                'sync_text': message}
            )
        else:
            if 'OK' in status:
                self.sudo().write({
                    'is_sync': True,
                    'sync_text': message}
                )
            else:
                self.sudo().write({
                    'is_sync': True,
                    'sync_text': message}
                )
