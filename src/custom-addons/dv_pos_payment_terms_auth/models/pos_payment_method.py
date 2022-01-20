from odoo import api, fields, models, _


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    needs_authorization_code = fields.Boolean(
        string='# Transacción requerida')
    use_payment_terms = fields.Boolean(string='Usar plazo de pago')
    payment_term_ids = fields.Many2many(
        'account.payment.term', string='Plazo de pago')
