import json
import logging

from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
import urllib3
import requests

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    dte_send_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('accepted', 'Accepted'),
            ('error', 'Error'),
            ('queue', 'In Queue')
        ], string="DTE Status", default='pending', tracking=True
    )
    dte_send_error = fields.Char(string="Send Errors", tracking=True)

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
                continue
            if not move.state == 'posted':
                continue
            if not config:
                msg = "DTE Client Configuration Missing: Company (%s)" % (move.company_id.name)
                raise UserError(msg)
            if not config.enabled:
                _logger.info("DTE Synchronization Disabled")
                return
            journal_dict = {}
            journal_dict['39'] = "BEL"
            journal_dict['33'] = "FAC"
            journal_dict['56'] = "N/D"
            journal_dict['61'] = "N/C"
            journal_id = journal_dict.get(move.l10n_latam_document_type_id.code, "XXX")
            dte_to_send = {
                "CLIENT": {
                    "client-vat-company": "CL%s" % (move.company_id.vat)
                },
                "INVOICE": {
                    "company_id": "CL91041000-8",
                    "date_invoice": "%s" % (move.invoice_date or fields.Date.context_today(move)),
                    "date_due": "%s" %(move.invoice_date_due),
                    "partner_id": "CL%s" % (move.partner_id.vat),
                    "type": "out_invoice",
                    "name": move.name,
                    "number": move.name,
                    "narration": move.narration,
                    "class_id": move.l10n_latam_document_type_id.code,
                    "journal_id": journal_id,
                    "total": "%s" % (move.amount_total)
                },
                "REFERENCE": [],
                "PARTNER": {
                    "name": move.partner_id.name,
                    "vat": "CL%s" % (move.partner_id.vat),
                    "street": move.partner_id.street,
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
                _logger.info(["TAXES", invoice_line.tax_ids, ",".join([x.dte_service_code or 'ERR' for x in invoice_line.tax_ids])])
                if invoice_line.tax_ids:
                    ivals["invoice_line_tax_ids"] = ",".join([x.dte_service_code or 'ERR' for x in invoice_line.tax_ids])
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
            if move.l10n_latam_document_type_id.code == '61':
                for ref in move.l10n_cl_reference_ids:
                    rvals = {}
                    rvals["name"] = ref.origin_doc_number
                    rvals["code"] = ref.reference_doc_code
                    rvals["class_id"] = ref.l10n_cl_reference_doc_type_selection
                    rvals["motive"] = ref.reason
                    rvals["date"] = str(ref.date)
                    dte_to_send["REFERENCE"].append(rvals)
            print(dte_to_send)
            payload = json.dumps(dte_to_send)
            http_pool = urllib3.PoolManager()
            header = {}
            header["Accept"] = "application/json"
            header["Content-Type"] = "application/json"
            # header["Body"] = payload
            url = config.server_base_url.strip("/") + "/boleta.electronica.envio"
            # url = config.server_base_url.strip("/") + "/boleta.electronica.semilla"
            print(["URL", url])
            try:
                response = requests.request("POST", url, headers=header, data=payload)
            except Exception as errstr:
                move.dte_send_status = "error"
                move.dte_send_error = errstr
                response = None
                msg = "Error sending document: %s" %(errstr)
                _logger.error(msg)
                if not config.pass_error:
                    raise UserError(msg)

            # response = requests.get("https://www.google.com")
            # response = http_pool.request("POST", url, headers=header)
            # response = http_pool.request("GET", url, headers=header)
            # try:
            if True and response:
                print(dir(response))
                print(response.content)
                print(response.status_code)
                response_json = json.loads(response.content.decode())
                print([type(response_json), response_json])
                result = json.loads(response_json.get("result", {}))
                print([type(result), result])
                error_code = result.get("ErrorCode", "")
                error_description = result.get("ErrorDescription", "")
                if error_code:
                    move.dte_send_status = "queue"
                    if not config.pass_error:
                        raise UserError("DTE Service Error: %s - %s" % (error_code, error_description))
                if response and response.status_code != '200':
                    print(response.raise_for_status())
                    move.dte_send_status = "sent"
                    move.dte_send_error = ""

            # except BaseException as errstr:
            #     msg = "Error sending document: "
            #     msg += "\nURL:%s" % (url)
            #     msg += "\nMethod: POST"
            #     msg += "\nHEADER: %s " % (header.keys())
            #     msg += "\n%s " % (errstr)
            #     raise UserError(msg)
        return True
