from odoo import api, fields, models


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Account Move or Invoice'
    _inherit = ['account.move']

    principal_company = fields.Many2one('res.company', string="Principal company", compute='_compute_principal_company',
                                        store=True)

    @api.depends('principal_company', 'invoice_line_ids')
    def _compute_principal_company(self):
        for rec in self:
            if rec.invoice_line_ids:
                rec.principal_company = rec.invoice_line_ids[0].principal_company
            else:
                rec.principal_company = False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    principal_company = fields.Many2one('res.company', string="Principal company")
