from odoo import models, api, fields
import logging

class WizardStockInventoryImport(models.TransientModel):
    _name = 'wizard.stock.inventory.import'
    _description = 'Wizard de Stock Import from SAP'

    location_id = fields.Many2one(
        'stock.location', string="Location Stock",
        domain="[('ccu_inventory_sync', '=', True)]",
        required=True)

    def action_inventory_import(self):
        self.ensure_one()
        print(['location_id: ', self.location_id.id])
        self.env['stock.inventory'].sudo().cron_esb_get_inventory(self.location_id.id)