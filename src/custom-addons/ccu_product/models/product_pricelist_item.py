from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class LimitPurchaseConfig:
    MONTHLY = "Monthly"
    DAILY = "Daily"
    CUSTOM = "Custom"

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    max_quantity = fields.Integer(
        string = "Max quantity",
        help = "Max quantity to apply pricelist modifier",
        default = 0
    )
    max_quantity_check = fields.Boolean(
        string = "Max quantity check",
        default = False
    )
    max_qty_options = fields.Selection([
        (LimitPurchaseConfig.MONTHLY, 'Monthly'),
        (LimitPurchaseConfig.DAILY, 'Daily'),
        (LimitPurchaseConfig.CUSTOM, 'Custom')],
        string='Max quantity options',
        default=LimitPurchaseConfig.MONTHLY,
        required=True
    )
    max_qty_init_date = fields.Datetime(
        string = "Initial date"
    )
    max_qty_end_date = fields.Datetime(
        string = "End date"
    )
    
    @api.model
    def create(self, vals):
        product_id = vals.get('product_tmpl_id') or vals.get('product_id')
        self._delete_duplicate(product_id, vals['pricelist_id'])
        return super(ProductPricelistItem, self).create(vals)

    def write(self, vals):
        product_id = vals.get('product_tmpl_id') or vals.get('product_id')
        pricelist_id = self.pricelist_id.id
        if product_id and len(self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id),('product_tmpl_id', '=', product_id)])) > 0:
            raise ValidationError(_("Pricelist's items must be unique per product"))
        return super(ProductPricelistItem, self).write(vals)  

    def _delete_duplicate(self, product_id, pricelist_id):
        if product_id:
            self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id),('product_tmpl_id', '=', product_id)]).unlink()
            self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_id),('product_id', '=', product_id)]).unlink()

    @api.constrains('max_quantity')
    def _check_min_max_quantity(self):
        if self.max_quantity <= 0 and self.max_quantity_check:
            raise ValidationError(_('Max quantity must be bigger than 0.'))
    
    @api.constrains('max_qty_init_date', 'max_qty_end_date')
    def _validate_max_qty_dates(self):
        if self.max_qty_init_date >= self.max_qty_end_date and self.max_quantity_check and self.max_qty_options == 'Custom':
            raise ValidationError(_('Init date must be earlier than End date.'))

