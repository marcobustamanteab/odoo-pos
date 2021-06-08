from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # l10n_cl_dte_voucher_service_provider = fields.Selection(related='company_id.l10n_cl_dte_voucher_service_provider', readonly=False,
    #                                                 help='Please select your company service provider for Voucher DTE service.')

    @api.model
    def set_values(self):
        company = self.company_id or self.env.company
        company.sudo().update({'l10n_cl_dte_voucher_service_provider':self.l10n_cl_dte_voucher_service_provider})
        super(ResConfigSettings, self).set_values()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.company_id or self.env.company
        service = company.l10n_cl_dte_voucher_service_provider
        res.update(l10n_cl_dte_voucher_service_provider=service)
        return res
