#encoding: utf-8
from odoo import api, fields, models

class ResHoliday(models.Model):
    # _inherit = ['res.partner']
    _name = "res.holiday"
    _description = "Holidays Definition"

    name = fields.Char()
    date = fields.Date()
    country_id = fields.Many2one("res.country", string="Country")