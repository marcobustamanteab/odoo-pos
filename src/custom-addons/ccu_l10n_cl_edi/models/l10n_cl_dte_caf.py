from odoo import models, fields, api

class L10NClDteCaf(models.Model):
    _inherit = 'l10n_cl.dte.caf'

    last_used_number = fields.Integer("Last Used", compute="_compute_remain", store=True)
    remain_qty = fields.Integer("Qty. Remain", compute="_compute_remain", store=True)
    remain_percent = fields.Float("% Remain", compute="_compute_remain", store=True)

    def _compute_remain(self):
        for record in self:
            am_list = self.env['account.move'].search(
                [
                    ('l10n_latam_document_type_id','=',record.l10n_latam_document_type_id.id),
                ]
            ).mapped('l10n_latam_document_number')
            am_list = [x for x in am_list if record.start_nb <= int(x) <= record.final_nb]
            print(["NUMBERS", ", ".join(sorted([str(x) for x in am_list]))])
            record.last_used_number = max([int(x) for x in am_list])
            record.remain_qty = record.final_nb - record.last_used_number
            if record.last_used_number >= record.start_nb:
                record.remain_percent = (record.final_nb - record.last_used_number) * 100 / ((record.remain_qty) or 1)
