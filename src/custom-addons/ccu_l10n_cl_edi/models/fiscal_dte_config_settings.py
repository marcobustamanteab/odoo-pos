from odoo import models, api, fields


class FidcslDTEConfigSettings(models.Model):
    _name = 'fiscal.dte.config.settings'
    _description = 'Fiscal DTE Custom Config Settings'

    name = fields.Char("Name", compute="_compute_name")
    company_id = fields.Many2one('res.company', string='Company"')
    # l10n_cl_dte_voucher_service_provider = fields.Many2one('fiscal.dte.service.provider',
    #                                                        string='Prepare DTE Server',
    #                                                        help='Please select your company service provider for voucher DTE service.')
    l10n_cl_dte_voucher_service_provider_post = fields.Many2one('fiscal.dte.service.provider',
                                                           string='Server for POST Send ',
                                                           help='Please select your company service provider for voucher DTE service.')
    l10n_cl_use_last_token = fields.Boolean('Use Last Token')

    def _compute_name(self):
        for rec in self:
            rec.name = rec.company_id.name + " - Config. Settings"