# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models
from datetime import date, datetime
from calendar import monthrange

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    reference_price = fields.Float(string="Precio de Referencia", digits=(8,1),
                                     required=False, help="Precio de Mercado del producto")

    def write(self, values):
        if 'list_price' in values:
            if int(values.get('list_price')) == 0:
                values['is_published'] = False
        res = super(ProductTemplate, self).write(values)
        return res
    
    def _get_limit_date_buy_max(self, item):
        if item.max_qty_options == 'Monthly':
            today = datetime.today()
            last_day_month = monthrange(today.year, today.month)[1]
            beginning = today.replace(day = 1)
            end = today.replace(day = last_day_month)
        elif item.max_qty_options == 'Daily':
            today = datetime.today()
            beginning = datetime(today.year, today.month, today.day)
            end = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)
        else:
            beginning = item.max_qty_init_date
            end = item.max_qty_end_date
        return beginning, end

    def _calculate_limit_amount_purchase(self, pricelist_items, partner):
        if len(pricelist_items) > 0 and pricelist_items[0].max_quantity_check:
            item = pricelist_items[0]
            if item.max_qty_options == 'Custom' and not (item.max_qty_init_date <= datetime.today() and datetime.today() <= item.max_qty_end_date):
                return {'bought': 0, 'left': 'dont-apply'}
            max_quantity = item.max_quantity
            beginning, end = self._get_limit_date_buy_max(item)
            orders = partner.sale_order_ids.filtered(lambda x: 
                x.state in ['sale', 'done'] and x.date_order >= beginning and x.date_order <= end
            ).ids
            lines = self.env['sale.order.line'].search([
                ('order_partner_id', '=', partner.id), 
                ('order_id', 'in', orders),
                ('product_id', '=', self.product_variant_ids.id)
            ])
            bought_amount = sum([line.product_uom_qty for line in lines])
            return {'bought': bought_amount, 'left': max_quantity - bought_amount}
        else:
            return {'bought': 0, 'left': 'dont-apply'}

    def get_monthly_buy_max(self, partner):
        res_pricelist = partner.property_product_pricelist
        pricelist_items = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', res_pricelist.id),
            '|', ('product_id', '=', self.product_variant_ids.id),
            ('product_tmpl_id', '=', self.id)
        ])
        return self._calculate_limit_amount_purchase(pricelist_items, partner)        
