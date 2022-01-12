# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one(
        "res.city", string="City of Address",
        compute='_get_current_city', inverse='_set_current_city',
        help="Computed field depending on the city of the related partner "
        "to the company")

    def _get_current_city(self):
        """Gets the current city of the related partner to the company"""
        self.city_id = self.partner_id.city_id

    def _set_current_city(self):
        """Sets the current city of the partner related to the company"""
        self.partner_id.city_id = self.city_id

    @api.onchange('city_id')
    def _onchange_city_id(self):
        """Completes the address information depending on the selected city"""
        if self.city_id:
            self.city = self.city_id.state_id.name
            self.zip = self.city_id.zipcode
            parent_id = self.city_id.state_id.parent_id
            self.state_id = parent_id.id if parent_id else self.city
        else:
            self.city = False
            self.zip = False
            self.state_id = False
