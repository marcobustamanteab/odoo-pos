import datetime

import uuid
import logging
import json
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.misc import formatLang, format_date, get_lang

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_sync = fields.Boolean(string='Synchronize', default=False, readonly=True,
                             tracking=True)
    sync_uuid = fields.Char(string='Sync. UUID', readonly=True, index=True, tracking=True,
                            default=lambda self: str(uuid.uuid4()))
    posted_payload = fields.Text('Posted Payload', readonly=True, copy=False)
    sync_reference = fields.Char(string='Sync. Text', readonly=True, tracking=True, copy=False)
    response_payload = fields.Text('Response Payload', readonly=True, copy=False)

    def prepare_partner_sap_codes(self):
        plist = []
        for line in self.line_ids:
            if line.partner_id.id not in plist:
                plist.append(line.partner_id.id)
        send_date = datetime.datetime.now().strftime("%Y%m%d")
        branch_ccu_code = self.invoice_user_id.sale_team_id.branch_ccu_code

        for pid in plist:
            partner = self.env['res.partner'].browse(pid)
            sap_code = ''
            if not partner.generic_sap_code:
                client = self._get_data_client_from_esb(partner.vat, send_date)
                if client:
                    sap_code = self._set_client_sap_code(partner.id, client['CODE'])
                else:
                    # CREAR CLIENTE EN SAP
                    new_client = self._add_client_to_SAP(partner, send_date, branch_ccu_code)
                    if new_client:
                        sap_code = self._set_client_sap_code(partner.id, new_client['CODE'])
                    else:
                        print('ERROR: New Client SAP Error')
            else:
                if self.partner_id and not sap_code:
                    raise ValidationError('ERROR in Client Creation of SAP')
                else:
                    print('Assent without Client')

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        for rec in self:
            rec.esb_send_account_move()
        return res

    # @job
    def esb_send_account_move(self):
        self.ensure_one()
        if not self.sync_uuid:
            print(["UUID", uuid.uuid4()])
            self.write({'sync_uuid': str(uuid.uuid4())})

        self.prepare_partner_sap_codes()

        payload_lines = []
        branch_ccu_code = self.invoice_user_id.sale_team_id.branch_ccu_code
        send_date = datetime.datetime.now().strftime("%Y%m%d")
        document_date = self.date.strftime("%Y%m%d")

        if not branch_ccu_code:
            raise ValidationError(
                'User of the movement does not belong to a work team or the team does not have a CCU Center code'
            )

        payload = {
            "HEADER": {
                "ID_MENSAJE": self.sync_uuid,
                "MENSAJE": "Account Movements from Odoo",
                "FECHA": send_date,
                "SOCIEDAD": self.company_id.ccu_business_unit,
                "LEGADO": "ODOO-POS",
                "CODIGO_INTERFAZ": "RTR038_Odoo"
            },
            "DOCUMENT_POST": {
                "HEAD": {
                    "CENTRO": self.invoice_user_id.sale_team_id.branch_ccu_code,
                    "FOLIO": self.name,
                    "CLDOC": self.journal_id.ccu_code,
                    "FEDOC": document_date,
                    "GLOSA": self.ref or self.name or '',
                    "MONTOT": self.amount_total,
                    "MONEDA": self.currency_id.name
                },
                "ASSENT": payload_lines
            }
        }

        i = 0
        for line in self.line_ids:
            i = i + 1

            # Jerarquía de Centro de Costos, primero el PARTNER luego la CUENTA
            cost_center = line.partner_id.cost_center_code if (
                    line.account_id.send_cost_center and line.partner_id.cost_center_code) else ''
            cost_center = line.account_id.default_cost_center_code if (
                    line.account_id.send_default_cost_center and line.account_id.default_cost_center_code) else cost_center

            # Jerarquía de Centro de Beneficios, primero el PARTNER luego la CUENTA
            profit_center = self.invoice_user_id.sale_team_id.profit_center_code if (
                    line.account_id.send_profit_center and self.invoice_user_id.sale_team_id.profit_center_code) else ''
            profit_center = line.account_id.default_profit_center_code if (
                    line.account_id.send_default_profit_center and line.account_id.default_profit_center_code) else profit_center

            partner = line.partner_id or self.partner_id
            sap_code = partner.sap_code
            vat = partner.vat
            if partner.use_generic_sap_client:
                sap_code = partner.generic_sap_code
                vat = partner.generic_RUT
            if line.account_id.send_client_sap_default_code:
                sap_code = line.account_id.default_sap_code

            if self.partner_id and not sap_code:
                raise ValidationError('ERROR in Client Creation of SAP')
            else:
                print('Assent without Client')

            special_major = "Y" if line.account_id.send_client_sap else 'N'
            line_amt = (line.debit - line.credit)

            alloc_nbr = ''
            if line.pos_order_id:
                alloc_nbr = line.pos_order_id.name
            else:
                if self.pos_order_id:
                    alloc_nbr = self.pos_order_id.name
                else:
                    if line.move_id.pos_session_id:
                        alloc_nbr = line.move_id.pos_session_id.name
                    else:
                        if self.pos_session_id:
                            alloc_nbr = self.pos_session_id.name
            ref_key_1 = line.ref
            if ref_key_1 and "Reversa" in str(ref_key_1):
                ref_key_1 = self.name
            payload_lines.append({
                "ITEMNO": str(i),
                "ACCOUNT": line.account_id.ccu_code or '',
                "RUTDNI": vat or '',
                "CODE": sap_code or '',
                "MAYOR": special_major,
                "GLOSA": line.account_id.send_fixed_text or line.name,
                "CECO": cost_center,
                "CEBE": profit_center,
                "MATERIAL": line.product_id.default_code or '',
                "CANTIDAD": line.quantity,
                "TOTAL": line_amt,
                "ALLOCNBR": alloc_nbr if not line.account_id.send_blank_allocation else '',
                "REF_KEY_1": ref_key_1 or '',
            })
            # TODO: No enviar ALLOCNBR cuando se tiene check en la cuenta - Transferencia Bancaria
            # TODO: Agregar descripción específica en el campo GLOSA configurarlo en la cuenta
            # TODO: REF_KEY_1 - Deposito - Nro. de Colilla
            #                   Transferencia Bancaria - RUT
            #                   Transbank - No enviamos nada
            #                   Valores a Depositar - mismos datos de la cuenta cargo y abono (venta).
            #                   Cheque - Nro. de Colilla Deposito

        # grabo payload y referencia UUID
        json_object = json.dumps(payload, indent=4)
        # print(json_object)

        # self.write({
        #     'posted_payload': json_object,
        #     'sync_uuid': sync_uuid}
        # )
        self.write({'posted_payload': json_object})

        esb_api_endpoint = '/sap/contabilidad/asiento/crear'
        backend = self.company_id.backend_esb_id

        res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        # print(json.dumps(res, indent=4))
        try:
            dcto_sap = int(res['mt_response']['respuesta']['documento_sap'])
            if dcto_sap > 0:
                self.write({
                    'is_sync': True,
                    'sync_reference': str(dcto_sap),
                    'response_payload': json.dumps(res, indent=4)}
                )
            else:
                json_object = json.dumps(payload, indent=4)
                json_object_response = json.dumps(res, indent=4)
                msg = "SAP response with error\n input data:\n" + json_object + "\nOUTPUT:\n" + json_object_response
                raise ValidationError(msg)
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
                BUPARTNER = resp.get('BUPARTNER', '')
                if BUPARTNER:
                    _logger.info('Client exist: ', BUPARTNER)
                    sap_client = {
                        'RUT': self.partner_id.vat,
                        'CODE': BUPARTNER
                    }
                    return sap_client
                else:
                    print('Client ID NOT found')
                    return False
            else:
                print('Client NOT exist')
                return False
        else:
            print('Invalidad ESB response')
            return False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_sync = fields.Boolean(string='Is sync with external account system?', related='move_id.is_sync', store=True)
    sync_uuid = fields.Char(string='Unique ID of sync', related='move_id.sync_uuid', store=True)
    posted_payload = fields.Text('Posted Payload', related='move_id.posted_payload', store=True)
    sync_reference = fields.Char(string='Sync with this text', related='move_id.sync_reference', store=True)
    reference_key_1 = fields.Char(string="Referencia 1")
