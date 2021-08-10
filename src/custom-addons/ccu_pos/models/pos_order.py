from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _

class PosOrder(models.Model):
    _name = 'pos.order'
    _description = 'Point of Sale Order'
    _inherit = ['pos.order']

    sequence_prefix = fields.Char("Cash Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=lambda x: x.config_id.prefix.strip(
                                      '/') if x.config_id.prefix else 'XXXXX')

    def _compute_sequence_prefix(self):
        for rec in self:
            rec.sequence_prefix = rec.config_id.prefix.strip('/') if rec.config_id.prefix else 'XXXXX'
