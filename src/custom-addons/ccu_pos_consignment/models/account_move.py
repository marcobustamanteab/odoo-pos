from odoo import api, fields, models


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Account Move or Invoice'
    _inherit = ['account.move']

    principal_company = fields.Many2one('res.company', string="Principal company", compute='_compute_principal_company',
                                        store=True)
    is_liquidated = fields.Boolean(string="Is Liquidated?")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    principal_company = fields.Many2one('res.company', string="Principal company")
