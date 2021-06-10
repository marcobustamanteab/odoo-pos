from odoo import models, fields, api


class DTEClientConfir(models.Model):
    _name = 'dte.client.config'
    _description = "DTE Client Configuration"

    name = fields.Char(string="Name")
    company_id = fields.Many2one("res.company", string="Company")
    server_base_url = fields.Char("Base Server URL")

    @api.onchange('company_id')
    def _onchange_cid_mode(self):
        self.name = "%s - %s" % (self.company_id.name, "Client Config.")
