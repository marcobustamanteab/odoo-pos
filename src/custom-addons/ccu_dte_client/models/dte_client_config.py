import json

import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class DTEClientConfig(models.Model):
    _name = 'dte.client.config'
    _description = "DTE Client Configuration"

    name = fields.Char(string="Name")
    company_id = fields.Many2one("res.company", string="Company")
    server_base_url = fields.Char("Base Server URL", required=True)
    pass_error = fields.Boolean("Pass Errors")
    enabled = fields.Boolean("Enabled")
    status_watch_service = fields.Boolean('Status Watch Service')

    @api.onchange('company_id')
    def _onchange_cid_mode(self):
        self.name = "%s - %s" % (self.company_id.name, "Client Config.")

    @api.model
    def create(self, vals):
        res = super(DTEClientConfig, self).create(vals)
        self.check_status_watch_service(vals.get('status_watch_service', False))
        return res

    def write(self, vals):
        res = super(DTEClientConfig, self).write(vals)
        if 'status_watch_service' in vals.keys():
            self.check_status_watch_service(vals.get('status_watch_service', False))
        return res

    def check_status_watch_service(self, activate):
        service_name = "Xerox Status Watch Service - %s" % (self.company_id.name)
        ir_cron = self.env["ir.cron"].sudo().search([('name', '=', service_name)])
        if ir_cron:
            ir_cron.write({'active': activate})
        else:
            if activate:
                ir_cron = self.env["ir.cron"]
                vals = {}
                vals["name"] = service_name
                vals["model_id"] = self.env.ref("ccu_dte_client.model_dte_client_config").id
                vals["interval_number"] = 5
                vals["interval_type"] = "minutes"
                vals["numbercall"] = -1
                vals["priority"] = 5
                vals["doall"] = True
                vals["code"] = "model.run_xerox_status_watch_scheduler(%s)" % (self.company_id.id)
                ir_cron.sudo().create(vals)

    @api.model
    def run_xerox_status_watch_scheduler(self, company_id):
        _logger.info("STEP 1: UPDATE SEND STATUS")
        issuer_company = self.env['res.company'].browse(company_id)
        if not issuer_company:
            _logger.error('Issuer Company Not Found')
            return
        config = self.env['dte.client.config'].search([('company_id', '=', company_id)])
        if not config:
            _logger.error("DTE Client Configuration Not Found")
            return
        acc_moves = self.env['account.move'].search(
            [
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('state', '=', 'posted'),
                ('dte_send_status', '!=', 'sent'),
                ('xerox_status', '=', 'pending'),
            ]
        )
        _logger.info("Sent Status Verification, Invoices to Process: %s" % (len(acc_moves)))

        url = config.server_base_url.strip("/") + "/boleta.electronica.envio.estado"

        inv_list = {}
        for acc in acc_moves:
            inv_list[acc.name] = acc.id
        header = {}
        header["Accept"] = "application/json"
        header["Content-Type"] = "application/json"
        dte_to_send = {
            "CLIENT": {
                "client-vat-company": "%s%s" % (issuer_company.country_id.code, issuer_company.vat)
            },
            "INVOICE_LIST": list(inv_list.keys())
        }
        payload = json.dumps(dte_to_send)

        try:
            response = requests.request("GET", url, headers=header, data=payload)
        except Exception as errstr:
            response = None
            msg = "Error Consulting Invoice Status: %s" % (errstr)
            _logger.error(msg)
            if not config.pass_error:
                raise UserError(msg)
        updates = 0
        if response:
            response_json = json.loads(response.content.decode())
            result = response_json.get("result", {})
            for inv_name in result.get('Object', {}).get('Invoices', {}).keys():
                invoice = self.env['account.move'].browse(inv_list.get(inv_name, -1))
                if invoice:
                    status = result.get('Object', {}).get('Invoices', {}).get(inv_name)
                    if invoice.dte_send_status != 'sent' and status.get('Status', '') == "REC":
                        invoice.write(
                            {
                                'dte_send_status': 'sent',
                                'xerox_id': status.get('Xerox Id', '')
                            }
                        )
                        updates += 1
        _logger.info("Invoices updated: %s" % (updates))
        _logger.info("STEP 2: UPDATE XEROX STATUS")

        acc_moves = self.env['account.move'].search(
            [
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('state', '=', 'posted'),
                ('dte_send_status', '=', 'sent'),
                ('xerox_status', '=', 'pending'),
            ]
        )
        _logger.info("Sent Status Verification, Invoices to Process: %s" % (len(acc_moves)))

        url = config.server_base_url.strip("/") + "/boleta.electronica.estado"

        inv_list = {}
        for acc in acc_moves:
            inv_list[acc.name] = acc.id
        # print(inv_list.keys())
        header = {}
        header["Accept"] = "application/json"
        header["Content-Type"] = "application/json"
        dte_to_send = {
            "CLIENT": {
                "client-vat-company": "%s%s" % (issuer_company.country_id.code, issuer_company.vat)
            },
            "INVOICE_LIST": list(inv_list.keys())
        }
        payload = json.dumps(dte_to_send)

        try:
            response = requests.request("GET", url, headers=header, data=payload)
        except Exception as errstr:
            response = None
            msg = "Error Consulting Invoice Status: %s" % (errstr)
            _logger.error(msg)
            if not config.pass_error:
                raise UserError(msg)
        updates = 0
        if response:
            response_json = json.loads(response.content.decode())
            result = response_json.get("result", {})
            # print(result.get('Object', {}).get('Invoices', {}).keys())
            for inv_name in result.get('Object', {}).get('Invoices', {}).keys():
                status = result.get('Object', {}).get('Invoices', {}).get(inv_name)
                # _logger.info(["INVOICE STATUS", inv_name, status.get('Xerox Status'), status.get('Date Sign')])
                # print(status.get('Xerox Status', '') != "pending")
                if status.get('Xerox Status', '') != "pending":
                    # print("Invoice Id", inv_list.get(inv_name, -1))
                    invoice = self.env['account.move'].browse(inv_list.get(inv_name, -1))
                    # print("Invoice",invoice )
                    if invoice:
                        if invoice.xerox_status == 'pending':
                            invoice.write(
                                {
                                    'xerox_status': status.get('Xerox Status'),
                                    'date_sign': status.get('Date Sign')
                                }
                            )
                            updates += 1
        _logger.info("Invoices updated: %s" % (updates))