import json
import logging

from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import urllib3
import requests
from ..helpers.api_helper import ApiHelper

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    dte_send_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('queue', 'In Queue'),
            ('error', 'Error'),
            # ('accepted', 'Accepted'),
        ], string="DTE Send Status", default='pending', tracking=True, copy=False,
        help="Send Status between Odoo ETD Client and Odoo ETD Service"
    )
    dte_send_error = fields.Char(string="Send Errors", tracking=True, copy=False)
    date_sign = fields.Datetime(
        "Signature Date",
        copy=False,
        track_visibility='onchange',
        help="""Empty if the document has not been signed. Filled in when the
            document is signed or sent for signature. Used to avoid signing or
            sending the same document twice."""
    )
    xerox_id = fields.Char("Xerox Id", copy=False)
    xerox_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('queue', 'In Queue'),
            ('error', 'Error'),
            ('generated', 'File Generated'),
            ('result', 'Result OK'),
            ('validated', 'Validated'),
            ('printed', 'Printed'),
            ('sii', 'Internal Tax Services'),
        ], string='Xerox Status', default='pending', copy=False
    )
    sii_status = fields.Char("ITS Status")
    printer_code = fields.Char("Printer Queue Code")

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        self.perform_send_dte()
        return res

    def action_perform_send_dte(self):
        self.perform_send_dte()

    def perform_send_dte(self):
        if len(self) == 0:
            _logger.info("len(self) == 0")
            return
        for move in self:
            config = move.env["dte.client.config"].search(
                [
                    ('company_id', "=", move.company_id.id)
                ]
            )
            if move.move_type not in ['out_invoice', 'out_refund']:
                _logger.warning("MOVE TYPE not out_invoice or out_refund")
                continue
            if not move.state == 'posted':
                _logger.warning("MOVE TYPE not posted")
                continue
            if not config:
                msg = "DTE Client Configuration Missing: Company (%s)" % (move.company_id.name)
                _logger.warning(msg)
                raise UserError(msg)
            if not move.partner_id.city_id:
                msg = "Partner city fields is incomplete (partner: %s)" % (move.partner_id.name)
                _logger.warning(msg)
                raise UserError(msg)
            if not move.partner_id.state_id.country_id.code or not move.partner_id.state_id.code:
                msg = "Partner Data Error: undefined city o state (partner: %s)" % (move.partner_id.name)
                _logger.warning(msg)
                raise UserError(msg)
            if not config.enabled:
                _logger.info("DTE Synchronization Disabled")
                return
            # journal_dict = {}
            # journal_dict['39'] = "BEL"
            # journal_dict['33'] = "FAC"
            # journal_dict['56'] = "N/D"
            # journal_dict['61'] = "N/C"
            # journal_id = journal_dict.get(move.l10n_latam_document_type_id.code, "XXX")
            partner = move.partner_shipping_id or move.partner_id
            journal_id = move.l10n_latam_document_type_id.doc_code_prefix or "XXX"
            dte_to_send = {
                "CLIENT": {
                    "client-vat-company": "%s%s" % (move.company_id.country_id.code, move.company_id.vat)
                },
                "INVOICE": {
                    "company_id": "%s%s" % (move.company_id.country_id.code, move.company_id.vat),
                    "date_invoice": "%s" % (move.invoice_date or fields.Date.context_today(move)),
                    "date_due": "%s" % (move.invoice_date_due),
                    "partner_id": "%s%s" % (move.partner_id.country_id.code, move.partner_id.vat),
                    "type": "out_invoice",
                    "name": move.name,
                    "number": move.name,
                    "narration": move.narration,
                    "departure_address": move.departure_address,
                    "departure_city": move.departure_city,
                    "departure_state": move.departure_state,
                    "vehicle_name": '',
                    "transport_name": '',
                    "transport_vat": '',
                    "transport_ref": '',
                    "delivery_address": " ".join([partner.street or '', partner.street2 or '']),
                    "delivery_city": partner.city_id.name,
                    "delivery_state": partner.city,
                    "class_id": move.l10n_latam_document_type_id.code,
                    "journal_id": journal_id,
                    "printer_code": move.printer_code,
                    "total": "%s" % (move.amount_total)
                },
                "REFERENCE": [],
                "PARTNER": {
                    "name": move.partner_id.name,
                    "vat": "CL%s" % (move.partner_id.vat),
                    "street": move.partner_id.street,
                    "city": move.partner_id.city,
                    "state_id": "%s%s" % (move.partner_id.state_id.country_id.code, move.partner_id.state_id.code),
                    "activity_description": move.partner_id.l10n_cl_activity_description,
                    "mobile": move.partner_id.mobile,
                    "email": move.partner_id.l10n_cl_dte_email or move.partner_id.email or '',
                    "country_id": move.partner_id.country_id.code
                },
                "DETAIL": [],
                "PRODUCT": []
            }
            for invoice_line in move.invoice_line_ids:
                product_id_code = ''.join(i for i in invoice_line.product_id.default_code or '000000' if i.isdigit())
                ivals = {}
                ivals["product_id"] = product_id_code or "000000"
                ivals["quantity"] = invoice_line.quantity
                ivals["price_unit"] = invoice_line.price_unit
                ivals["name"] = invoice_line.name or invoice_line.product_id.name
                ivals["account_id"] = invoice_line.account_id.code
                # ivals["display_type"] = "product"
                # ivals["ref_etd"] = product_id_code or "000000"
                ivals["discount"] = invoice_line.discount
                _logger.info(["TAXES", invoice_line.tax_ids,
                              ",".join([x.dte_service_code or 'ERR' for x in invoice_line.tax_ids])])
                if invoice_line.tax_ids:
                    ivals["invoice_line_tax_ids"] = ",".join(
                        [x.dte_service_code or 'ERR' for x in invoice_line.tax_ids])
                else:
                    ivals["invoice_line_tax_ids"] = "EX"
                dte_to_send["DETAIL"].append(ivals)

                pvals = {}
                pvals["default_code"] = product_id_code or '000000'
                pvals["name"] = invoice_line.product_id.name
                pvals["type"] = invoice_line.product_id.type
                pvals["ref_etd"] = product_id_code or '000000'
                pvals["description"] = invoice_line.product_id.description
                dte_to_send["PRODUCT"].append(pvals)
            if move.l10n_latam_document_type_id.internal_type in ('debit_note', 'credit_note'):
                for ref in move.l10n_cl_reference_ids:
                    rvals = {}
                    rvals["name"] = ref.origin_doc_number
                    rvals["code"] = ref.reference_doc_code
                    rvals["class_id"] = ref.l10n_cl_reference_doc_type_selection
                    rvals["motive"] = ref.reason
                    rvals["date"] = str(ref.date)
                    dte_to_send["REFERENCE"].append(rvals)
            # print(dte_to_send)
            _logger.info("SENDING DTE to DTE Service: %s" % (dte_to_send))
            payload = json.dumps(dte_to_send)
            http_pool = urllib3.PoolManager()
            header = {}
            header["Accept"] = "application/json"
            header["Content-Type"] = "application/json"
            # header["Body"] = payload
            url = config.server_base_url.strip("/") + "/boleta.electronica.envio"
            # url = config.server_base_url.strip("/") + "/boleta.electronica.semilla"
            _logger.info(["URL", url])
            try:
                response = ApiHelper(move.company_id.id).post(url, headers=header, data=payload,
                                                              oauth2_required=config.oauth2)
            except Exception as errstr:
                move.dte_send_status = "error"
                move.dte_send_error = errstr
                response = None
                msg = "Error sending document: %s" % (errstr)
                _logger.error(msg)
                if not config.pass_error:
                    raise UserError(msg)

            # response = requests.get("https://www.google.com")
            # response = http_pool.request("POST", url, headers=header)
            # response = http_pool.request("GET", url, headers=header)
            # try:
            if True and response:
                # _logger.info(dir(response))
                # _logger.info(response.content)
                # _logger.info(response.status_code)
                response_json = json.loads(response.content.decode())
                # _logger.info([type(response_json), response_json])
                result = response_json.get("result", {})
                # _logger.info([type(result), result])
                error_code = result.get("ErrorCode", "")
                error_description = result.get("ErrorDescription", "")
                if error_code:
                    move.write({
                        'dte_send_status': 'error',
                        'dte_send_error': error_description,
                    })
                    if not config.pass_error:
                        raise UserError("DTE Service Error: %s - %s" % (error_code, error_description))
                else:
                    # if response and response.status_code != '200':
                    _logger.info(response.raise_for_status())
                    vals = {}
                    vals["dte_send_status"] = 'sent'
                    vals["dte_send_error"] = ''
                    if result.get('Object', {}).get('Invoice', {}).get('xerox_id', '') != 'queue':
                        vals["xerox_id"] = result.get('Object', {}).get('Invoice', {}).get('xerox_id', '')
                    move.write(vals)
            # except BaseException as errstr:
            #     msg = "Error sending document: "
            #     msg += "\nURL:%s" % (url)
            #     msg += "\nMethod: POST"
            #     msg += "\nHEADER: %s " % (header.keys())
            #     msg += "\n%s " % (errstr)
            #     raise UserError(msg)
        return True

    def perform_send_dte_massive(self):
        config = self.env['dte.client.config'].search([('company_id', '=', self.company_id.id)])
        if not config:
            _logger.info('DTE Client Configuration Not Found')
            return
        print(["ACTIVE_IDS", self.env.context.get('active_ids', [])])
        invoices = self.env['account.move'].search(
            [
                ('id', 'in', (self.env.context.get('active_ids', []))),
                ('state', '=', 'posted'),
                ('dte_send_status', 'in', ('pending','error'))
            ]
        )
        _logger.info("Invoice to Process: %s" % (len(invoices)))
        if config:
            if config.enabled:
                for inv in invoices:
                    inv.perform_send_dte()
        return True
