from odoo import api, models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    is_sync = fields.Boolean(string='Is sync with external account system?', related='picking_id.is_sync', store=True)
    sync_uuid = fields.Char(string='Unique ID of sync', related='picking_id.sync_uuid', store=True)
    posted_payload = fields.Text('Posted Payload', related='picking_id.posted_payload', store=True)
    sync_text = fields.Text(string='Sync with this text', related='picking_id.sync_text', store=True)
