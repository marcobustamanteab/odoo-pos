#encoding: utf-8
from odoo import fields, models, api

class FiscalDTELog(models.Model):
    _name = "fiscal.dte.log"
    _description = "Log for Fiscal DTE Events"
    _order = 'create_date desc'

    name = fields.Char("Name", compute="_compute_name")
    model_id = fields.Many2one("ir.model", string="Model")
    model_name = fields.Char("Name")
    event_name = fields.Char("Event Name")
    event_description = fields.Char("Event Description")
    event_data = fields.Text("Event Data")

    def _compute_name(self):
        for record in self:
            record.name = "%s / %s (%s) " %(record.model_id.name, record.model_name, record.id)

    @api.model
    def register_log(self, model_id, model_name, name, description, data):
        new_log = self.env[self._name]
        vals = {}
        vals["model_id"] = model_id
        vals["model_name"] = model_name
        vals["event_name"] = name
        vals["event_description"] = description
        vals["event_data"] = data

