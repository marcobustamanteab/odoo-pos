#encoding: utf-8
from odoo import api, fields, models

class ProductProperty(models.Model):
    # _inherit = ['res.partner']
    _name = "product.property"
    _description = "Product Property"

    code = fields.Char("Code")
    name = fields.Char("Name")
    display_name = fields.Char("Display Name", compute="_compute_display_name", store=True, index=True)
    parent_id = fields.Many2one("product.property", string="Parent Property")
    show_in_card = fields.Boolean("Show in Item Card")
    show_in_filter = fields.Boolean("Show in Filter")
    color = fields.Integer(string='Color Index')
    url = fields.Char("Icon URL")

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name or ""
            if record.parent_id.display_name:
                record.display_name = " / ".join([record.parent_id.display_name, record.name])
