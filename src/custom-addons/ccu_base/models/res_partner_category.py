from odoo import fields, models, api


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    daily_limit = fields.Integer('Daily limit')
    weekly_limit = fields.Integer('Weekly limit')
    daily_exception_limit = fields.Integer('Daily exception limit')
    purchase_calendar = fields.Char('Purchase calendar', help='''Este campo está compuesto por 7 caracteres que representan los días de compra durante la semana. El primer carácter corresponde al día Lunes y el último al Domingo. N indica que no se permite comprar, mientras que S sí permite comprar. Por ejemplo, si quisieramos definir que un cliente que no puede comprar durante los fines de semana, entonces se debe setear este campo de la siguiente forma: SSSSSNN''')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

