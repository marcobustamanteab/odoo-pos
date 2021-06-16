
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
        sync_uuid = str(uuid.uuid1())
        year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
        fecha_AAAAMMDD = str((year * 10000) + (month * 100) + day)
        year, month, day, hour, min = map(int, self.date.strftime("%Y %m %d %H %M").split())
        fecha_dcto = str((year * 10000) + (month * 100) + day)
        branch_ccu_code = self.create_uid.sale_team_id.branch_ccu_code
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
                    "LEGADO": "Odoo",
                    "CODIGO_INTERFAZ": "RTR038_Odoo"
                },
                "DOCUMENT_POST": {
                    "HEAD": {
                        "RUTDNI": "",
                        "CENTRO": branch_ccu_code,
                        "FOLIO": self.name,
                        "CLDOC": self.journal_id.ccu_code, # "IE" tipo de documento
                        "FEDOC": fecha_dcto,
                        "GLOSA": self.ref,
                        "MONTOT": self.amount_total,
                        "MONEDA": self.currency_id.name
                    },
                    "ASSENT": payload_lines
                }
            }

            accounts = self.mapped('line_ids.account_id').filtered('ccu_sync')
            lines = [x for x in self.line_ids if x.account_id in accounts]

            i = 0
            for idx, line in enumerate(lines, start=1):
                i = i + 1
                base_currency = line.currency_id or line.company_currency_id
                base_amt = line.amount_currency or (line.debit - line.credit)
                line_currency = line.company_currency_id
                line_amt = (line.debit - line.credit)

                # analytic_code = (
                #     line.analytic_account_id.code or (if line.account_id.code == '11403' or )
                #     self.company_id.esb_default_analytic_id.code)
                ceco = line.analytic_account_id.ccu_code or ''
                payload_lines.append({
                    "ITEMNO": str(i),
                    "ACCOUNT": line.account_id.ccu_code,
                    "GLOSA": line.name,
                    "CECO": ceco,
                    "CEBE": '',
                    "MATERIAL": line.product_id.default_code or '',
                    "CANTIDAD": line.quantity,
                    "TOTAL": line_amt
                })

            #grabo payload y referencia UUID
            json_object = json.dumps(payload, indent=4)
            self.write({
                'posted_payload': json_object,
                'sync_uuid': sync_uuid}
            )

            esb_api_endpoint = '/sap/contabilidad/asiento/crear'
            backend = self.company_id.backend_esb_id
            print(json_object)
            res = backend.api_esb_call("POST", esb_api_endpoint, payload)
            print(json.dumps(res))
            try:
                dcto_sap = int(res['mt_response']['respuesta']['documento_sap'])
                if dcto_sap > 0:
                    self.write({
                        'is_sync': True,
                        'sync_reference': str(dcto_sap)}
                    )
            except KeyError:
                json_object = json.dumps(res['mt_response']['respuesta'], indent=4)
                print(json_object)
                raise ValidationError("SAP response with error, review input data")


    @api.model
    def send_account_move_to_ESB(self):
        if self.journal_id.type != 'bank' and self.journal_id.ccu_sync:
            print('Sending JOB QUEUE for Account Move ID: ', self.id)
            self.with_delay(channel='root.account').esb_send_account_move()

    def update_sync(self, message='none'):
        txt = str(self.id)
        print(            'Response from ESB, JOB QUEUE for Account Move: ', txt)
        self.sudo().write({
            'is_sync': True,
            'sync_reference': message}
        )
