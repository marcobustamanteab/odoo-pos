# -*- coding: utf-8 -*-

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('city_id')
    def _onchange_city_id(self):
        """Completes the address information depending on the selected city.
        Overwrites the original onchange method of base_address_city module"""
        if self.city_id:
            self.city = self.city_id.state_id.name
            self.zip = self.city_id.zipcode
            parent_id = self.city_id.state_id.parent_id
            self.state_id = parent_id.id\
                if parent_id else self.city_id.state_id
        else:
            self.city = False
            self.zip = False
            self.state_id = False


    def onchange_city_id(self):
        self._onchange_city_id()
