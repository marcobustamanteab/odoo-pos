from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"
    ccu_code = fields.Char(string='SAP Account Number')
    send_cost_center = fields.Boolean(string="Send Cost Center to SAP", default=False)
    send_profit_center = fields.Boolean(string="Send profit Center to SAP", default=False)
    send_client_sap = fields.Boolean(string="Send Client Code to SAP account movements", default=False)
