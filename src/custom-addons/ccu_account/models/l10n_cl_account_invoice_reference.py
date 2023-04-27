from odoo import api, models, fields

class l10nclAccountInvoiceReference(models.Model):
    _inherit = 'l10n_cl.account.invoice.reference'


    def name_get(self):
        res = []
        for rec in self:
            val = dict(rec._fields['l10n_cl_reference_doc_type_selection'].selection).get(
                rec.l10n_cl_reference_doc_type_selection)
            name = f'{val} - {rec.origin_doc_number}'
            res.append((rec.id, name))
        return res