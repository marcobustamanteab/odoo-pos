from odoo import api, fields, models
from odoo.exceptions import ValidationError
import uuid
import time
import logging
import json

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_sync = fields.Boolean(string='Is sync with external account system?', default=False, readonly=True)
    sync_uuid = fields.Char(string='Unique ID of sync', readonly=True, index=True)
    posted_payload = fields.Text('Posted Payload', readonly=True)
    sync_reference = fields.Char(string='Sync with this text', readonly=True)

    #    @job
    def esb_send_account_move(self):
        self.ensure_one()
        payload_lines = []
        sync_uuid = str(uuid.uuid4())
        year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
        fecha_AAAAMMDD = str((year * 10000) + (month * 100) + day)
        year, month, day, hour, min = map(int, self.date.strftime("%Y %m %d %H %M").split())
        fecha_dcto = str((year * 10000) + (month * 100) + day)
        branch_ccu_code = self.invoice_user_id.sale_team_id.branch_ccu_code

        pos_prefix = ''
        pos_order = self.env['pos.order'].search([('name', '=ilike', self.ref)], limit=1)
        if len(self.pos_order_ids) > 0:
            pos_prefix = self.pos_order_ids[0].session_id.config_id.sequence_id.prefix
        else:
            pos_session = self.env['pos.session'].search([('name', '=ilike', self.ref)], limit=1)
            if pos_session:
                pos_prefix = pos_session[0].config_id.sequence_id.prefix
            else:
                pos_prefix = self.ref

        pos_name = pos_prefix.strip('/') if pos_prefix else 'XXXX'
        transbak_id = self.env['pos.payment'].search([('pos_order_id', '=', pos_order.id)], limit=1).transaction_id
        text = self.ref or self.name or ''

        if not branch_ccu_code:
            raise ValidationError(
                'User of the movement does not belong to a work team or the team does not have a CCU Center code'
            )
        else:
            payload = {
                "HEADER": {
                    "ID_MENSAJE": sync_uuid,
                    "MENSAJE": "Account Movements from Odoo",
                    "FECHA": fecha_AAAAMMDD,
                    "SOCIEDAD": self.company_id.ccu_business_unit,
                    "LEGADO": "ODOO-POS",
                    "CODIGO_INTERFAZ": "RTR038_Odoo"
                },
                "DOCUMENT_POST": {
                    "HEAD": {
                        "CENTRO": branch_ccu_code,
                        "FOLIO": self.name,
                        "CLDOC": self.journal_id.ccu_code,
                        "FEDOC": fecha_dcto,
                        "GLOSA": text,
                        "MONTOT": self.amount_total,
                        "MONEDA": self.currency_id.name
                    },
                    "ASSENT": payload_lines
                }
            }

            # accounts = self.mapped('line_ids.account_id').filtered('ccu_sync')
            # lines = [x for x in self.line_ids if x.account_id in accounts]

            i = 0
            for line in self.line_ids:
                i = i + 1
                base_currency = line.currency_id or line.company_currency_id
                base_amt = line.amount_currency or (line.debit - line.credit)
                line_currency = line.company_currency_id
                line_amt = (line.debit - line.credit)

                cost_center = ''
                if line.account_id.send_cost_center:
                    cost_center = line.partner_id.cost_center_code

                if line.account_id.send_default_cost_center and line.account_id.default_cost_center_code:
                    cost_center = line.account_id.default_cost_center_code

                profit_center = ''
                if line.account_id.send_profit_center:
                    profit_center = self.invoice_user_id.sale_team_id.profit_center_code

                if line.account_id.send_default_profit_center and line.account_id.default_profit_center_code:
                    profit_center = line.account_id.default_profit_center_code

                sap_code = line.partner_id.sap_code
                if not sap_code and line.partner_id:
                    client = self._get_data_client_from_esb(line.partner_id.vat, fecha_AAAAMMDD)
                    print(client)
                    if client:
                        sap_code = self._set_client_sap_code(line.partner_id.id, client['CODE'])
                    else:
                        # CREAR CLIENTE EN SAP
                        new_client = self._add_client_to_SAP(line.partner_id, fecha_AAAAMMDD, branch_ccu_code)
                        if new_client:
                            sap_code = self._set_client_sap_code(line.partner_id.id, new_client['CODE'])
                        else:
                            print('ERROR: New Client SAP Error')
                else:
                    if self.partner_id and not sap_code:
                        raise ValidationError(
                            'ERROR in Client Creation of SAP'
                        )
                    else:
                        print('Assent without Client')

                if line.account_id.send_client_sap_default_code:
                    CODE = line.account_id.default_sap_code
                else:
                    CODE = sap_code

                MAYOR = "Y" if line.account_id.send_client_sap else 'N'

                if transbak_id:
                    GLOSA = line.name + 'TBKID: ' + transbak_id
                else:
                    GLOSA = line.name

                payload_lines.append({
                    "ITEMNO": str(i),
                    "ACCOUNT": line.account_id.ccu_code or '',
                    "RUTDNI": line.partner_id.vat or '',
                    "CODE": CODE or '',
                    "MAYOR": MAYOR,
                    "GLOSA": GLOSA,
                    "CECO": cost_center,
                    "CEBE": profit_center,
                    "MATERIAL": line.product_id.default_code or '',
                    "CANTIDAD": line.quantity,
                    "TOTAL": line_amt,
                    "ASING": pos_name
                })

            # grabo payload y referencia UUID
            json_object = json.dumps(payload, indent=4)
            self.write({
                'posted_payload': json_object,
                'sync_uuid': sync_uuid}
            )

            esb_api_endpoint = '/sap/contabilidad/asiento/crear'
            backend = self.company_id.backend_esb_id
            print(json_object)
            res = backend.api_esb_call("POST", esb_api_endpoint, payload)
            print(json.dumps(res, indent=4))
            try:
                dcto_sap = int(res['mt_response']['respuesta']['documento_sap'])
                if dcto_sap > 0:
                    self.write({
                        'is_sync': True,
                        'sync_reference': str(dcto_sap)}
                    )
            except KeyError:
                json_object = json.dumps(payload, indent=4)
                json_object_response = json.dumps(res, indent=4)
                msg = "SAP response with error\n input data:\n" + json_object + "\nOUTPUT:\n" + json_object_response
                raise ValidationError(msg)

    @api.model
    def send_account_move_to_ESB(self):
        if self.journal_id.type != 'bank' and self.journal_id.ccu_sync:
            print('Sending JOB QUEUE for Account Move ID: ', self.id)
            self.with_delay(channel='root.account').esb_send_account_move()

    def action_send_account_move_to_esb(self):
        self.send_account_move_to_ESB()

    def update_sync(self, message='none'):
        txt = str(self.id)
        print('Response from ESB, JOB QUEUE for Account Move: ', txt)
        self.sudo().write({
            'is_sync': True,
            'sync_reference': message}
        )

    def _set_client_sap_code(self, partner_id, sap_code):
        vals = {
            'sap_code': sap_code,
        }
        partner = self.env['res.partner'].browse(partner_id)
        if partner:
            partner.write(vals)
            return partner.sap_code

    def _get_data_client_from_esb(self, rut, fecha_AAAAMMDD):
        esb_api_endpoint = "/sap/cliente/consultar"

        payload = {
            "HEADER": {
                "ID_MENSAJE": str(uuid.uuid4()),
                "MENSAJE": "From Odoo POS Client Search",
                "FECHA": fecha_AAAAMMDD,
                "SOCIEDAD": self.company_id.ccu_business_unit,
                "LEGADO": "ODOO-POS",
                "CODIGO_INTERFAZ": "CREAR_CLIENTE_SAP_PO"
            },
            "CLIENTE": {
                "RUTDNI": rut,
                "CENTRO": ""
            }
        }

        # invocación al servicio REST
        backend = self.company_id.backend_esb_id
        print('BUSCANDO CLIENTE EN SAP...')
        print(json.dumps(payload, indent=4))
        res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        print(json.dumps(res, indent=4))
        # solo si respuesta tiene datos proceso con la syncronización
        if res:
            resp = res['mt_response']['Result']
            if resp == 'Y':
                name = res['mt_response']['BP']['BP']['NOMBRE']
                _logger.info(
                    'Client exist: ',
                    name)
                sap_client = {
                    'RUT': res['mt_response']['BP']['BP']['RUTDNI'],
                    'CODE': res['mt_response']['BP']['BP']['CODE']
                }
                return sap_client
            else:
                print('Client NOT exist')
                return False
        else:
            print('Invalidad ESB response')
            return False

    def _add_client_to_SAP(self, partner, fecha_AAAAMMDD, branch_ccu_code):
        esb_api_endpoint = "/sap/cliente/crear"

        FINTR = 1 if partner.l10n_cl_sii_taxpayer_type == 1 else 2
        TRATAM = '0005' if partner.l10n_cl_sii_taxpayer_type == 1 else '0002'

        payload = {
            "HEADER": {
                "ID_MENSAJE": str(uuid.uuid4()),
                "MENSAJE": "From Odoo POS Client Create",
                "FECHA": fecha_AAAAMMDD,
                "SOCIEDAD": self.company_id.ccu_business_unit,
                "LEGADO": "ODOO-POS",
                "CODIGO_INTERFAZ": "CREAR_CLIENTE_SAP_PO"
            },
            "BP": {
                "FINTR": FINTR,
                "TRATAM": TRATAM,
                "NOMBRE": partner.name,
                "APELLIDO": "",
                "RUTDNI": partner.vat,
                "CALLE": partner.street,
                "CODPOS": "",
                "COMUNA": partner.city,
                "REGION": int(partner.state_id.code),
                "PAIS": partner.country_id.code,
                "TELEF1": partner.mobile,
                "TELEF2": partner.phone,
                "EMAIL": partner.email
            },
            "DATOS_VENTA": {
                "CENTRO": branch_ccu_code,
                "CONPA": "ZN00",
            },
            "DATOS_IMPUESTO": {
                "MWST": "1",
                "J1CA": "1",
                "J2CA": "1",
                "J3CA": "1",
                "Z1CA": "1",
                "Z2CA": "1",
                "Z3CA": "1",
            }
        }

        # invocación al servicio REST
        backend = self.company_id.backend_esb_id
        print('CREANDO CLIENTE EN SAP...')
        print(json.dumps(payload, indent=4))
        res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        print(print(json.dumps(res, indent=4)))
        # solo si respuesta tiene datos proceso con la syncronización
        if res:
            resp = res['mt_response']['RESPUESTA']
            if resp:
                BUPARTNER = resp['BUPARTNER']
                if BUPARTNER:
                    _logger.info(
                        'Client exist: ',
                        BUPARTNER)
                    sap_client = {
                        'RUT': self.partner_id.vat,
                        'CODE': BUPARTNER
                    }
                    return sap_client
                else:
                    return False
            else:
                print('Client NOT exist')
                return False
        else:
            print('Invalidad ESB response')
            return False
