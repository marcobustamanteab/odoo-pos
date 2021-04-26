from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    
    order = fields.Integer(
        string="Order in ecommerce NavBar",
        help="Determines the order to show the categories on NavBar, must be unique per main categories"
    )
    
    main_category = fields.Boolean(
        string="Main Category",
        help="Determines if this category is on e-commerce's navbar"
    )
    is_highlighted = fields.Boolean(
        string="Category is highlighted",
        help="Category is highlighted if checked"
    )
    
    @api.constrains('order')
    def _validate_order(self):
        categories_orders = self.env['product.public.category'].search([
            ('main_category', '!=', False),
            ('id', '!=', self.id)]
        ).mapped('order')
        if self.order < 1:
            raise ValidationError(_('Order must be bigger than 0'))
        if self.order in categories_orders:
            raise ValidationError(_('Order must be unique. Already taken %s') % sorted(categories_orders))