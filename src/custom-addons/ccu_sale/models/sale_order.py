# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            res = super(SaleOrder, order).action_confirm()
            partner = self.env['res.partner'].search([('id', '=', order.partner_id.id)], limit=1)
            if not partner.is_employee:
                partner.update_category()

        return res

    def _validate_order_stock(self, order):
        values = []
        for order_line in order.order_line:
            res = self._cart_update_check(order_line, None, True)
            warning_message = res.pop('error', False)
            if warning_message:
                values.append(warning_message)
        return values

    def _create_payment_transaction(self, vals):
        for order in self:
            partner = self.env['res.partner'].search([('id', '=', order.partner_id.id)], limit=1)
            if self.checkLimit(partner, order.amount_total + partner.monthly_purchase):
                raise UserError(_(
                    "This purchase exceeds the maximum amount allowed in a month"))
            else:
                self.updatePurchase(partner, order.amount_total)
        try:
            order = request.website.sale_get_order()
        except AttributeError:
            # When method is called from REST api, "website" is not present as an attribute on request
            order = self

        # Check product's stock
        errors = self._validate_order_stock(order)
        if errors:
            raise UserError(_(
                "Some products became unavailable and your cart has been updated. We're sorry for the inconvenience."))
        return super(SaleOrder, self)._create_payment_transaction(vals)

    def checkLimit(self, partner, purchase):
        if partner.category == 'vip-premium':
            return False
        elif partner.reached_limit:
            return True
        elif purchase >= partner.limit_purchase:
            return True
        else:
            return False

    def updatePurchase(self, partner, amount_total):
        partner.monthly_purchase = partner.monthly_purchase + amount_total
        partner.reached_limit = partner.monthly_purchase + amount_total >= partner.limit_purchase

    def _cart_update_check(self, line, line_id=None, without_line_id=False):
        values = {}
        if len(
                line.sudo().read()) > 0 and line.product_id.type == 'product' and line.product_id.inventory_availability in [
            'always', 'threshold']:
            cart_qty = sum(
                self.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
            max_product_buy = line.product_id.product_tmpl_id.get_monthly_buy_max(self.partner_id)
            check_min_stock = cart_qty > line.product_id.get_available_stock()
            not_string_limit_purchase = max_product_buy['left'] != 'dont-apply'
            check_limit_purchase = not_string_limit_purchase and cart_qty > max_product_buy['left']
            if check_min_stock or check_limit_purchase and (line_id == line.id or without_line_id):
                max_qty = max_product_buy['left']
                qty = line.product_id.get_available_stock()
                new_qty = min(qty, max_qty) if not_string_limit_purchase else qty
                if new_qty > 0:
                    line.warning_stock = _('You tried to add %s products but only %s are available') % (
                        cart_qty, new_qty)
                    values['error'] = line.warning_stock
                else:
                    self.warning_stock = _(
                        "Some products became unavailable and your cart has been updated. We're sorry for the inconvenience.")
                    values['error'] = self.warning_stock
                values['new_qty'] = new_qty
            else:
                line.warning_stock = ''
                self.warning_stock = ''
                values['error'] = self.warning_stock
        else:
            if len(line.read()) != 0:
                line.warning_stock = ''
            self.warning_stock = ''
            values['error'] = self.warning_stock
        return values

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        for order in self:
            values = super(SaleOrder, order)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
            line_id = values.get('line_id')
            for line in self.order_line:
                values = self._cart_update_check(line, line.id)
                new_qty = values.pop('new_qty', None)
                if new_qty != None:
                    new_val = super(SaleOrder, order)._cart_update(line.product_id.id, line.id, None, new_qty, **kwargs)
                    values.update(new_val)
            return values
