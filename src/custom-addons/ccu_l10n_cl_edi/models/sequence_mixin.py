from odoo import models


class SequenceMixin(models.AbstractModel):
    """Mechanism used to have an editable sequence number.
    Be careful of how you use this regarding the prefixes. More info in the
    docstring of _get_last_sequence.
    """
    _inherit = 'sequence.mixin'
    _description = "Automatic sequence"

    def _set_next_sequence(self):  # Odoo
        """Set the next sequence.

        This method ensures that the field is set both in the ORM and in the database.
        This is necessary because we use a database query to get the previous sequence,
        and we need that query to always be executed on the latest data.

        :param field_name: the field that contains the sequence.
        """
        self.ensure_one()
        last_sequence = self._get_last_sequence()
        # print(["GET_LAST_SEQUENCE", last_sequence])
        new = not last_sequence
        if new:
            last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

        format, format_values = self._get_sequence_format_param(last_sequence)
        # print(["FORMAT", format, format_values])
        if new:
            format_values['seq'] = 0
            format_values['year'] = self[self._sequence_date_field].year % (10 ** format_values['year_length'])
            format_values['month'] = self[self._sequence_date_field].month
        format_values['seq'] = format_values['seq'] + 1
        # OVERRIDE STANDARD NUMBER BECAUSE HAVE TO USE CAF'S RANGES
        if self._name == 'account.move' and self.move_type in ('out_invoice', 'out_refund'):
            # print("IS_INVOICE")
            caf_sequence = self.env['l10n_cl.dte.caf'].search(
                [
                    ('remain_qty', '>', '0'),
                    ('l10n_latam_document_type_id', '=', self.l10n_latam_document_type_id.id),
                ], order='sequence', limit=1
            )
            if caf_sequence:
                if caf_sequence.last_used_number == 0:
                    format_values['seq'] = caf_sequence.start_nb
                else:
                    format_values['seq'] = caf_sequence.last_used_number + 1
                # print(["CAF DISPONIBLE", caf_sequence[0].last_used_number])
        # print(["FORMAT VALUES", format_values])
        self[self._sequence_field] = format.format(**format_values)
        self._compute_split_sequence()
