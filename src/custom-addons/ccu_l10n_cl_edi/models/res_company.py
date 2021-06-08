from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    INVOICE_SERVER = "SIIINVSERVER"
    VOUCHER_SERVER = "SIIVCHSERVER"

    l10n_cl_dte_voucher_service_provider = fields.Selection([
        ('SIIINVSERVER', 'SII - Palena / Maullin'),
        ('SIIVCHSERVER', 'SII - ApiCert / Api')], 'DTE Service Provider for Vouchers',
        help='Please select your company service provider for voucher DTE service.')


