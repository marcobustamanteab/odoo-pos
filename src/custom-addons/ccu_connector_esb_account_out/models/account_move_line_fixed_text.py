from odoo import api, fields, models


class AccountMoveLineFixedText(models.Model):
    _name = 'account.move.line.fixed.text'
    _description = 'Fixed Text for Account Move Line'

    name = fields.Char(string="Fixed Text")