from odoo import fields, api, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    max_payment_amount = fields.Float("Max Value Control")