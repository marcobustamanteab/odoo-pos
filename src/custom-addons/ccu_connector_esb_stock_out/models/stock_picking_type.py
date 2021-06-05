# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    ccu_sync = fields.Boolean(string="Sync with ESB", default=False)
    ccu_code = fields.Char(string='ERP Origin Third-Party')
    ccu_code_controlled = fields.Char(string='ERP Origin Controlled Party')
    ccu_code_participated = fields.Char(
        string='ERP Origin Participated Party')
    ccu_code_usage = fields.Char(string='ERP Usage Code', size=3)

