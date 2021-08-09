from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"
    ccu_code = fields.Char(string='SAP Account Number')
    send_cost_center = fields.Boolean(string="Send cost center", default=False)
    send_profit_center = fields.Boolean(string="Send profit center", default=False)
    send_client_sap = fields.Boolean(string="Send SAP client code", default=False)
    send_client_sap_default_code = fields.Boolean(string="Send default SAP client Code", default=False)
    default_sap_code = fields.Char(string='Default client code')
    send_default_cost_center = fields.Boolean(string="Send default cost center code", default=False)
    default_cost_center_code = fields.Char(string='Default cost center code')