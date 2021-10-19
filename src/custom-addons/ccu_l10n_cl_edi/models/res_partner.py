# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    l10n_cl_dte_email = fields.Char(string='DTE Email', required=True)
    l10n_cl_activity_description = fields.Char(string='Activity Description', required=True)
