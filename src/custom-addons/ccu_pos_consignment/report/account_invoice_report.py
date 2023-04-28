from odoo import models

class AccountInvoiceReport(models.AbstractModel):
    _inherit = 'report.ccu_l10n_cl_edi.generic_invoice_report'
    _name = 'report.ccu_l10n_cl_edi.account_invoice_report'
