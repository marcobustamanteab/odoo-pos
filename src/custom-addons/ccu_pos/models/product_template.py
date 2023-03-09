# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    principal_company = fields.Many2one('res.company', string="Principal company")
