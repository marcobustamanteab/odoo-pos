# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    principal_company = fields.Many2one('res.company', string="Principal company")

    def write(self, values):
        if 'principal_company' in values.keys() and values['principal_company']:
            if ((not self.company_id) and 'company_id' not in values.keys()) or (
                    not self.company_id and 'company_id' in values.keys() and not values['company_id']):
                raise ValidationError(_("Please set the company in order to set the principal company"))
        if 'company_id' in values.keys() and not values['company_id']:
            if self.principal_company or ('principal_company' in values.keys() and values['principal_company']):
                raise ValidationError(_("Please set the company in order to set the principal company"))
        return super().write(values)
