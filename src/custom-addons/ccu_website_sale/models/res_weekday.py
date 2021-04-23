#encoding: utf-8
from odoo import api, fields, models

class ResWeekDay(models.Model):
    # _inherit = ['res.partner']
    _name = "res.weekday"
    _description = "Days of the Week"

    name = fields.Char()
    day_id = fields.Integer()