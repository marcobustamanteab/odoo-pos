# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import json
import logging, time, uuid, json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class Inventory(models.Model):
    _inherit = "stock.inventory"

    #@job
    def esb_import_inventory(self, location, values):
        location.ensure_one()
        inventory_lines = []
        product_ids = []
        now = fields.Datetime.context_timestamp(
            self.env.user, fields.Datetime.now())

        # crea diccionario con campos de la respuesta del servicio REST
        values_dict = {str(line['Material']): line['Stock'] for line in values}

        print(['VALUES_DICT:', values_dict])
        products = self.env['product.product'].search([
            ('default_code', '!=', False),
            ('type', '=', 'product'),
            ('company_id', '=', location.company_id.id)])

        _logger.info(
            'Starting inventory adjustment for %d Odoo products.',
            len(products))
        print(products)
        for product in products:
            product_qty = float(values_dict.get(product.default_code, '0'))
            if product.tracking == 'serial' or product.tracking == 'lot':
                if product_qty == product.qty_available:
                    msg = _(
                        "Product %s quantity in ERP %d"
                        " is inconsistent with Odoo quantity %d.") % (
                              product.default_code,
                              product_qty,
                              product.qty_available)
                    _logger.warning(msg)
                    product.message_post(body=msg)
            else:
                print(['PRODUCT_ODOO', product.default_code, 'CANTIDAD EN ODOO: ', product.qty_available, 'CANTIDAD EN SAP:', product_qty,])
                if product_qty == product.qty_available:
                    _logger.debug(
                        "Product %s %s quantity %d unchanged, skipping.",
                        product.default_code,
                        product_qty)
                else:
                    new_qty = max(product_qty, 0)
                    inventory_lines.append((0, 0, {
                        'product_qty': new_qty,
                        'product_id': product.id,
                        'location_id': location.id
                    }))
                    _logger.debug(
                        "Product %s %s quantity changed from %d to %d.",
                        product.default_code,
                        product.qty_available,
                        new_qty)

        missing_products = [
            x for x in values_dict.keys()
            if x not in products.mapped('default_code')]
        if missing_products:
            _logger.warning(
                "These ERP products are missing from Odoo: %s",
                str(missing_products))
        _logger.info(
            "Adjusted inventory for %d Odoo products",
            len(inventory_lines))
        inventory_value = {
            'name': ('ERP Inventory Adjustment %s' % fields.Datetime.to_string(now)),
            'date': fields.Date.today(),
            'location_ids': [location.id],
            'state': 'confirm',
            'company_id': location.company_id.id,
            'line_ids': inventory_lines,
        }
        print(['INVENTARIO:'])
        print(inventory_value)
        inventory_rec = self.create(inventory_value)
        inventory_rec.action_validate()


    @api.model
    def cron_esb_get_inventory(self):
        id_mensaje = str(uuid.uuid4())
        year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
        fecha_AAAAMMDD = str((year*10000) + (month*100) + day)

        location_rec = self.sudo().env['stock.location'].search([('ccu_inventory_sync', '=', True),
                                                          ('ccu_code', '!=', False)])
        if location_rec:
            for location in location_rec:
                esb_api_endpoint = "/sap/inventario/stock/consultar"

                payload = {
                    "HEADER": {
                        "ID_MENSAJE": id_mensaje,
                        "MENSAJE": "TT09",
                        "FECHA": fecha_AAAAMMDD,
                        "SOCIEDAD": location.company_id.ccu_business_unit,
                        "LEGADO": "ODOO-POS",
                        "CODIGO_INTERFAZ": "ITD009_POS"
                    },
                    "DETAIL": [
                        {
                            "Centro": location.location_id.ccu_code,
                            "Almacen": location.ccu_code,
                            "Material": ""
                        }
                    ]
                }

                # invocación al servicio REST
                backend = location.company_id.backend_esb_id  # Parámetro con objeto Backend configurado con servidor WSO2

                res = backend.api_esb_call("POST", esb_api_endpoint, payload)
                # solo si respuesta tiene datos proceso con la syncronización
                if res:
                    values = res.get('mt_response', {}).get('DETAIL', {})
                    if values:
                        _logger.info(
                            'Sending stock update to JOB QUEUE for location: %s' % location.name)
                        self.with_delay(channel='root.inventory').esb_import_inventory(location, values)
                    else:
                        print('Not data y SAP response')
                else:
                    print('Invalidad ESB response')

