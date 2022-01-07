from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    truck_UEN_code = fields.Char(string='Unidad de Negocio TRUCK', index=True)
