#encoding: utf-8
from odoo import fields, models, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        # Avoid to post a vendor bill with a inactive currency created from the incoming mail
        for move in self.filtered(
                lambda x: x.company_id.country_id.code == "CL" and
                          x.company_id.l10n_cl_dte_service_provider in ['SII', 'SIITEST'] and
                          x.journal_id.l10n_latam_use_documents):
            # check if we have the currency active, in order to receive vendor bills correctly.
            if move.move_type in ['in_invoice', 'in_refund'] and not move.currency_id.active:
                raise UserError(
                    _('Invoice %s has the currency %s inactive. Please activate the currency and try again.') % (
                        move.name, move.currency_id.name))
            # generation of customer invoices
            if move.move_type in ['out_invoice', 'out_refund'] and move.journal_id.type == 'sale':
                new_log = move.env['fiscal.dte.log']
                vals = {}
                vals["model_id"] = move.env['ir.model'].search([('model','=',move._name)])[0].id
                vals["model_name"] = move.name
                vals["event_name"] = "DTE Created"
                vals["event_description"] = "DTE Created as attachment id %s" %(move.l10n_cl_sii_send_file.id)
                vals["event_data"] = ""
                new_log.create(vals)
        return res