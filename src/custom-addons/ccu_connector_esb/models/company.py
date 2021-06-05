# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ccu_business_unit = fields.Char(string="CCU Business Unit")
    backend_esb_id = fields.Many2one(
        "backend.acp", string="ESB Provider"
    )
    esb_default_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="ESB Default Analytic Account")
