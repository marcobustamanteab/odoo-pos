#encoding: utf-8
from odoo import api, fields, models

class ResCityDistrict(models.Model):
    # _inherit = ['res.partner']
    _name = "res.city.district"
    _description = "Communes of Chile"

    name = fields.Char()
    code = fields.Char()
    city_id = fields.Many2one("res.city", string="City")
    weekday_ids = fields.Many2many("res.weekday", string="Delivery Days")
    lead_time = fields.Integer()



