# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCity(models.Model):
    _inherit = 'res.city'

    code = fields.Char(
        help="City code")
    type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal'),
    ], default="normal", help="City type")
    l10n_cl_sii_regional_office = fields.Char(
        string="Regional Office",
        help="SII Regional Office associated to this city")
