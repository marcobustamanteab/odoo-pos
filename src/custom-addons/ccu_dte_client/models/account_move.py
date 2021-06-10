import json

from odoo import fields, api, models
from odoo.exceptions import UserError
import urllib3
import requests


class AccountMove(models.Model):
    _inherit = 'account.move'

    dte_send_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('accepted', 'Accepted'),
            ('error', 'Error'),
            ('queue', 'In Queue')
        ], string="DTE Status", default='pending'
    )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        print(["RES", res, res.name])
        config = self.env["dte.client.config"].search(
            [
                ('company_id', "=", self.company_id.id)
            ]
        )
        if not config:
            raise UserError("DTE Client Configuration Missing: Company (%s)" % (self.company_id.name))
        dte_to_send = {
            "CLIENT": {
                "client-vat-company": "CL%s" % (self.company_id.vat)
            },
            "INVOICE": {
                "company_id": "CL91041000-8",
                "invoice_date": "%s" % (self.invoice_date),
                "partner_id": "CL%s" % (self.partner_id.vat),
                "type": "out_invoice",
                "name": self.name,
                "journal_id": "%s" % (self.journal_id.dte_service_code)
            },
            "PARTNER": {
                "name": self.partner_id.name,
                "vat": "CL%s" % (self.partner_id.vat),
                "street": self.partner_id.street,
                "activity_description": self.partner_id.l10n_cl_activity_description,
                "phone": self.partner_id.phone,
                "email": self.partner_id.email,
                "country_id": self.partner_id.country_id.code
            },
            "DETAIL": [],
            "PRODUCT": []
        }
        for invoice_line in self.invoice_line_ids:
            ivals = {}
            ivals["product_id"] = invoice_line.product_id.default_code
            ivals["quantity"] = invoice_line.quantity
            ivals["price_unit"] = invoice_line.price_unit
            ivals["name"] = invoice_line.name or invoice_line.product_id.name
            ivals["account_id"] = invoice_line.account_id.code
            ivals["display_type"] = "product"
            ivals["discount"] = invoice_line.discount
            ivals["invoice_line_tax_ids"] = ",".join([x.dte_service_code for x in invoice_line.tax_ids])
            dte_to_send["DETAIL"].append(ivals)

            pvals = {}
            pvals["default_code"] = invoice_line.product_id.default_code
            pvals["name"] = invoice_line.product_id.name
            pvals["type"] = invoice_line.product_id.type
            pvals["description"] = invoice_line.product_id.description
            dte_to_send["PRODUCT"].append(pvals)
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
        response = requests.request("POST", url, headers=header, data=payload)
        # response = requests.get("https://www.google.com")
        # response = http_pool.request("POST", url, headers=header)
        # response = http_pool.request("GET", url, headers=header)
        # try:
        if True:
            print(dir(response))
            print(response.content)
            print(response.status_code)
            response_json = json.loads(response.content.decode())
            print([type(response_json), response_json])
            result = json.loads(response_json.get("result", {}))
            print([type(result),result])
            error_code = result.get("ErrorCode","")
            error_description = result.get("ErrorDescription","")
            if error_code:
                self.dte_send_status = "queue"
                if not config.pass_error:
                    raise UserError("DTE Service Error: %s - %s" %(error_code, error_description))
            if response and response.status_code != '200':
                print(response.raise_for_status())
        # except BaseException as errstr:
        #     msg = "Error sending document: "
        #     msg += "\nURL:%s" % (url)
        #     msg += "\nMethod: POST"
        #     msg += "\nHEADER: %s " % (header.keys())
        #     msg += "\n%s " % (errstr)
        #     raise UserError(msg)
        return res
