# Copyright 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResPartnerDistributionCenter(models.Model):
    """Partner Distribution Center object"""
    _name = "res.partner.distribution_center"
    _description = 'Partner Distribution Center (For Employees)'
    _order = "name asc"

    name = fields.Char(string='Name', help="Name", required=True)
    zone = fields.Char(string='Geographic Zone', help="Geographic Zone", required=True)
    type = fields.Char(string='Type', help="Type", required=True)
    type_description = fields.Char(string='Type Description', help="Type Description", required=True)
    x_coordenates = fields.Char(string='Coordenates (X)', help="Coordenates (X)", required=True)
    y_coordenates = fields.Char(string='Coordenates (Y)', help="Coordenates (Y)", required=True)
    street = fields.Char(string='Street', help="Street")
    street_number = fields.Char(string='Street Number', help="Street Number")
    commune_name = fields.Char(string='Commune Name', help="Commune Name")
    city_name = fields.Char(string='City Name', help="City Name")
    active = fields.Boolean(string="Is Employee", default=True)

