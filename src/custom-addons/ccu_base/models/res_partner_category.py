from odoo import fields, models, api


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    daily_limit = fields.Integer('Daily limit')
    weekly_limit = fields.Integer('Weekly limit')
    daily_exception_limit = fields.Integer('Daily exception limit')
    purchase_calendar = fields.Char('Purchase calendar')

