# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            res = super(SaleOrder, order).action_confirm()
            partner = self.env['res.partner'].search([('id', '=', order.partner_id.id)], limit=1)
            if not partner.is_employee:
                partner.update_category()

        return res
