# -*- coding: utf-8 -*-

from odoo import fields, models


class ResState(models.Model):
    _inherit = 'res.country.state'

    code = fields.Char(
        help="State code")
    complete_name = fields.Char(
        help="Complete name for the state")
    parent_id = fields.Many2one(
        'res.country.state', string="Parent", index=True,
        domain="[('type', '=', 'view'), ('id', '!=', id)]",
        help="Parent state")
    child_ids = fields.One2many(
        'res.country.state', 'parent_id', string="Childs",
        help="Childs states")
    type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal')
    ], default="normal", help="State type")
