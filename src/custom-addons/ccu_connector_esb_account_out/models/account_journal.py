# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    ccu_code = fields.Char(string='CCU Code')
    ccu_sync = fields.Boolean(string="Syncs with ESB", default=False)

    @api.constrains('ccu_sync', 'sequence_id')
    def _check_sequence_size(self):
        # ir.sequence
        for journal in self.filtered('ccu_sync'):
            raw_seq = '%s%s%s' % (
                (journal.sequence_id.prefix or ''),
                '0' * journal.sequence_id.padding,
                (journal.sequence_id.suffix or ''))
            seq = (
                raw_seq
                .replace('%(range_year)s', 'YYYY')
                .replace('%(year)s', 'YYYY'))
            if len(seq) > 10:
                raise ValidationError(_(
                    "Sequences for ESB synced journals can't have more than "
                    "ten digits. Sequence %s will have %d digits."
                    ) % (seq, len(seq)))
