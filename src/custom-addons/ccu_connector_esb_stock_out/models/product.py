# Copyright 2020 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    outgoing_code = fields.Char(string='Third-Party Out Code')
    outgoing_code_related = fields.Char(string='Related Party Out Code')
    outgoing_code_subsidiary = fields.Char(string='Subsidiary Party Out Code')
    outgoing_code_no_charge = fields.Char(string='No Charge Party Out Code', size=2)
    outgoing_code_substandard = fields.Char(string='Substandard Out Code', size=2)
    incoming_code = fields.Char(string='Third-Party In Code')
    incoming_code_related = fields.Char(string='Related Party In Code')
    incoming_code_subsidiary = fields.Char(string='Subsidiary Party In Code')
    incoming_code_no_charge = fields.Char(string='No Charge Party In Code', size=2)
    incoming_code_substandard = fields.Char(string='Substandard In Code', size=2)









