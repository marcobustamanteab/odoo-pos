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

    ticket_is_sync = fields.Boolean(string='Synchronize', default=False, readonly=True, copy=False,
                             tracking=True)
    ticket_sync_uuid = fields.Char(string='Sync. UUID', readonly=True, index=True, tracking=True, copy=False,
                            default=lambda self: str(uuid.uuid4()))
    ticket_sync_date = fields.Datetime(string="Sync date", readonly=True, index=True, tracking=True)
    ticket_posted_payload = fields.Text('Posted Payload', readonly=True, copy=False)
    ticket_response_payload = fields.Text('Response Payload', readonly=True, copy=False)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)

        for rec in self:
            rec.action_esb_send_ticket_to_esb()
        return res


    def action_esb_send_ticket_to_esb(self):
        print('Iniciando envío de Boleta a ESB')
        for rec in self:
            if rec.l10n_latam_document_type_id.code == '39' and rec.move_type in ['out_invoice', 'out_refund'] and rec.state not in ['canceled', 'draft']:
                rec.with_delay(channel='root.ticket_cunsumption').esb_send_ticket_to_esb()
            if rec.l10n_latam_document_type_id.code == '61':
                for ref_id in rec.l10n_cl_reference_ids:
                    if ref_id.l10n_cl_reference_doc_type_selection == '39':
                        rec.with_delay(channel='root.ticket_cunsumption').esb_send_ticket_to_esb()


    # @job
    def esb_send_ticket_to_esb(self):
        self.ensure_one()
        if self.ticket_is_sync:
            return

        backend = self.company_id.backend_esb_id
        if not backend.active:
            _logger.info("ESB Synchornization Service DISABLED")
            return

        print(self.amount_by_group)

        imp_adds = []
        tax_19 = 0
        tax_iaba = 0
        for tax_group in self.amount_by_group:
            group_id = tax_group[6]
            sii_imp_ADD_code = False
            sii_imp_ADD_base = False
            config = self.env['fiscal.dte.printing.config'].search([('company_id', '=', self.company_id.id)],
                                                                   limit=1)
            if group_id == config.tax_6_id.id:
                tax_19 = tax_group[1]
            else:
                tax_iaba = tax_group[1]
                imp = self.env['account.tax'].search([
                    ('company_id.id', '=', self.company_id.id),
                    ('tax_group_id', '=', group_id),
                ], limit=1)

                imp_adds.append({
                    'code': imp.l10n_cl_sii_code,
                    'base': imp.amount,
                    'amount': tax_iaba,
                })

        document_referenced_code = False
        for document_referenced in self.l10n_cl_reference_ids:
            document_referenced_code = document_referenced.l10n_cl_reference_doc_type_selection or ''

        payload = {
            "document": {
                    "BOLETA_UEN": int(self.company_id.truck_UEN_code) or 0,
                    "BOLETA_ENCABEZADOFOLIO": int(''.join([i for i in self.name if i.isdigit()])) or '', #332755650729,
                    "BOLETA_ESTADO": "GEN",
                    "BOLETA_FECHA": self.invoice_date.strftime('%Y-%m-%d %H:%M:%S'), #"2021/10/06 00:00:00",
                    "BOLETA_ENCABEZADOFECHAEM": self.invoice_date.strftime('%Y-%m-%d'), #"2021-06-10",
                    "BOLETA_ENCABEZADORAZONSOCIAL": self.partner_id.name,
                    "BOLETA_ENCABEZADOTOTAL": str(int(self.amount_total)), # "9200",
                    "BOLETA_NUMERO": int(''.join([i for i in self.name if i.isdigit()])) or '', #3557244,
                    "BOLETA_DIRECCION": self.partner_id.street, #"Independencia 565 0",
                    "BOLETA_RUT": self.partner_id.vat, # "17328188-9",
                    "BOLETA_IDECLAVE": "0", 
                    "BOLETA_COMUNA": self.partner_id.city_id.name or 'SANTIAGO',
                    "BOLETA_CIUDAD": self.partner_id.city,
                    "BOLETA_CODAUT": " ",
                    "BOLETA_TIPOPAGO": "0",#"TARJETA CREDITO",
                    "BOLETA_FONO": self.partner_id.phone or '0',
                    "BOLETA_CODMENSAJE": "0",
                    "BOLETA_IVA": int(tax_19),
                    "BOLETA_NETO": int(self.amount_untaxed) or 0,
                    "BOLETA_TOTAL": int(self.amount_total) or 0,
                    "BOLETA_TIPDOC": int(self.l10n_latam_document_type_id.code) or 0,
                    "BOLETA_TASAIVA": 19,
                    "BOLETA_EXENTO": 0,
                    "BOLETA_TIPODOCUMENTODEREFERENC": int(document_referenced_code) or 0
                }
            }
            #invoice_number = self.env['account.move'].search([('pos_order_id.id', '=', line.pos_order_id.id)], limit=1).name if line.pos_order_id else ''

        # grabo payload y referencia UUID
        json_object = json.dumps(payload, indent=4)
        print(json_object)  
        esb_api_endpoint = '/sii/consumo-folios/crear'

        res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        print(json.dumps(res, indent=4))
        try:
            status = res['STATUS']
            if status == "OK":
                self.write({
                    'ticket_sync_uuid': str(uuid.uuid4()),
                    'ticket_is_sync': True,
                    'ticket_sync_date': fields.datetime.now(),
                    'ticket_posted_payload': json_object,
                    'ticket_response_payload': json.dumps(res, indent=4)}
                )
            else:
                json_object = json.dumps(payload, indent=4)
                json_object_response = json.dumps(res, indent=4)
                msg = "ERROR TRUCK response with error\n input data:\n" + json_object + "\nOUTPUT:\n" + json_object_response
                raise ValidationError(msg)
        except KeyError:
            json_object = json.dumps(payload, indent=4)
            json_object_response = json.dumps(res, indent=4)
            msg = "ERROR TRUCK response with error\n input data:\n" + json_object + "\nOUTPUT:\n" + json_object_response
            raise ValidationError(msg)

