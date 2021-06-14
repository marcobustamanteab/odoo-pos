
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import uuid
import time
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    sync_uuid = fields.Char(string='Unique ID of sync', index=True)
    is_sync = fields.Boolean(string='Is sync with external account system?', default=False)
    sync_text = fields.Text(string='Sync with this text', readonly=True)
    posted_payload = fields.Char('Posted Payload')


#    @job
    def esb_send_account_move(self):
        self.ensure_one()
        payload_lines = []
        sync_uuid = str(uuid.uuid1())
        year, month, day, hour, min = map(int, time.strftime("%Y %m %d %H %M").split())
        fecha_AAAAMMDD = str((year * 10000) + (month * 100) + day)
        year, month, day, hour, min = map(int, self.date.strftime("%Y %m %d %H %M").split())
        fecha_dcto = str((year * 10000) + (month * 100) + day)
        #move_ref = self.name[-10:]

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
                    "CENTRO": "",
                    "FOLIO": self.name,
                    "CLDOC": self.journal_id.ccu_code,
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

            payload_lines.append({
                "ITEMNO": str(i),
                "ACCOUNT": line.account_id.ccu_code,
                "GLOSA": line.name,
                "CECO": "",
                "CEBE": line.analytic_account_id.ccu_code,
                "MATERIAL": line.product_id.default_code,
                "TX_KEY": "S/R",
                "CANTIDAD": line.quantity,
                "TOTAL": line_amt
            })

        #grabo payload y referencia UUID
        self.posted_payload = payload
        self.sync_uuid = sync_uuid

        esb_api_endpoint = '/sap/contabilidad/asiento/crear'
        backend = self.company_id.backend_esb_id
        print(payload)
        res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        print(res)
        msg = res['mt_response']['HEADER']['MENSAJE']
        if 'Recibido OK' not in msg:
            raise ValidationError(msg)




    # @api.multi
    # def post(self, invoice=False):
    #     res = super(AccountMove, self).post(invoice)
    #     for move in self:
    #         if move.journal_id.type != 'bank' and move.journal_id.ccu_sync:
    #             move.with_delay().esb_send_account_move()
    #     return res

    @api.model
    def send_account_move_to_ESB(self):
        if self.journal_id.type != 'bank' and self.journal_id.ccu_sync:
            _logger.info(
                'Sending JOB QUEUE for Account Move ID: ',
                self.id)
            self.with_delay(channel='root.account').esb_send_account_move()

    def update_sync(self, message='none'):
        txt = str(self.id)
        _logger.info(
            'Response from ESB, JOB QUEUE for Account Move: ',
            txt)
        self.sudo().write({
            'is_sync': True,
            'sync_text': message}
        )