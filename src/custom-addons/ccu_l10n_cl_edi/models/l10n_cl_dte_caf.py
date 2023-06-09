from odoo import models, fields, api


class L10NClDteCaf(models.Model):
    _inherit = 'l10n_cl.dte.caf'

    last_used_number = fields.Integer("Last Used", compute="_compute_remain")
    remain_qty = fields.Integer("Qty. Remain", compute="_compute_remain")
    remain_percent = fields.Float("% Remain", compute="_compute_remain")
    sequence = fields.Integer(string="CAF Sequence")

    def _compute_remain(self):
        for record in self:
            am_list = self.env['account.move'].search(
                [
                    ('company_id', '=', record.company_id.id),
                    ('l10n_latam_document_type_id', '=', record.l10n_latam_document_type_id.id),
                ]
            ).mapped('l10n_latam_document_number')
            am_list = [x for x in am_list if record.start_nb <= int(x) <= record.final_nb]
            if am_list:
                record.last_used_number = max([int(x) for x in am_list])
                record.remain_qty = record.final_nb - record.last_used_number
                if record.last_used_number >= record.start_nb:
                    record.remain_percent = (record.final_nb - record.last_used_number) * 100.0 / (
                                (record.final_nb - (record.start_nb -1)) or 1)
            else:
                record.last_used_number = 0
                record.remain_qty = record.final_nb - (record.start_nb - 1)
                record.remain_percent = 100
